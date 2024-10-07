import socket
import json
import threading
import time

if True:
    # A header will be sent first to determine the length of the message
    HEADER = 16
    # This is the port that the server will be listening on
    PORT = 50505
    # This is the IP address of the server
    SERVER = "127.0.0.1"
    # This is the address of the server - a tuple of the server and port
    ADDR = (SERVER, PORT)
    # This is the format that the server will be using
    FORMAT = "utf-8"
    # This is the message that will be sent so the server knows to disconnect
    DISCONNECT_MESSAGE = {
        "msg_type": "!DISCONNECT",
        "msg_subject": "",
        "msg_body": "",
        "recipients": [],
        "username": "",
    }

    NOTIFICATIONS = []
    NOTIFS_LOCK = threading.Lock()


def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    _username, _passcode = identify_user()

    runner = threading.Thread(target=run, args=(_username,))
    runner.start()
    listener = threading.Thread(target=listen)
    listener.start()


def run(_username):

    while True:

        choice = input(
            "\nChoose an option: 1: email, 2: text, 3: announcement, 4: check notifications, 5: disconnect, 6: get user list, 7: hack\n"
        )

        if choice == "1":
            email(_username)
        elif choice == "2":
            text(_username)
        elif choice == "3":
            announcement(_username)
        elif choice == "4":
            check_notifications()
        elif choice == "5":
            confirm = input("Are you sure you want to disconnect? (y/n): ")
            if confirm == "y":
                break
            continue
        elif choice == "6":
            get_user_list()
        elif choice == "7":
            hack()
        else:
            print("Invalid choice")

    print("-- disconnecting... --")
    send(json.dumps(DISCONNECT_MESSAGE))
    time.sleep(1)
    NOTIFS_LOCK.acquire()
    if DISCONNECT_MESSAGE in NOTIFICATIONS:
        NOTIFICATIONS.remove(DISCONNECT_MESSAGE)
    NOTIFS_LOCK.release()
    print("-- disconnected --")
    client.close()


def listen():
    print("-- listening for server messages... --")

    done = False
    while not done:
        msg = receive()
        if not msg:  # or msg["msg_body"] == "Message received":
            continue
        if msg["msg_type"] == "info":
            print(f"-- from server: {msg['msg_body']} --")
            continue
        if msg == DISCONNECT_MESSAGE:
            done = True
            print(f"-- from server: Disconnect confirmed --")
            continue
        if msg["msg_type"] == "hack":
            print(f"-- error: unkown error --")
            time.sleep(1)
            print(f"-- error: data breach --")
            time.sleep(1)
            print(msg["msg_subject"])
            print(msg["msg_body"])
            time.sleep(5)
            print("-- connection reestablished --")
            continue
        print("-- notification received --")
        NOTIFS_LOCK.acquire()
        NOTIFICATIONS.append(msg)
        NOTIFS_LOCK.release()

    print("-- no longer listening --")


def email(_username):
    recipients = []
    recipient = input(
        "Enter the recipients usernames one by one (press enter on empty to move on):\n"
    )
    while recipient != "":
        recipients.append(recipient)
        recipient = input()

    subject = input("Enter the subject: ")
    body = input("Enter the message body:\n")
    send(
        build_json_msg(
            "email",
            msg_body=body,
            msg_subject=subject,
            recipients=recipients,
            username=_username,
        )
    )
    print("-- email sent --")


def text(_username):
    recipients = [input("Enter the recipient's username: ")]

    body = input("\nEnter the message:\n")
    send(
        build_json_msg("text", msg_body=body, recipients=recipients, username=_username)
    )
    print("-- text sent --")


def announcement(_username):
    heading = input("Enter the heading: ")
    body = input("Enter the announcement body:\n")
    send(
        build_json_msg(
            "announcement", msg_body=body, msg_subject=heading, username=_username
        )
    )
    print("-- announcement sent --")


def check_notifications():
    notifs = []
    NOTIFS_LOCK.acquire()
    for notif in NOTIFICATIONS:
        notifs.append(notif)
    NOTIFICATIONS.clear()
    NOTIFS_LOCK.release()

    print("Notifications:")
    for notif in notifs:
        input("\nPress enter to see the next notification")
        print(
            f"\nNew {notif['msg_type']}{' from ' + notif['username'] if notif['msg_type'] in ['email', 'text'] else ''}:"
        )
        if notif["msg_subject"] != "":
            print(f"Subject: {notif['msg_subject']}")
        print(f"{notif['msg_type']}:\n{notif['msg_body']}")
        if notif["msg_type"] == "email":
            print(f"Recipients: {', '.join(notif['recipients'])}")

    input("\nNo more notifications. Press enter to return to the main menu")
    print()


def get_user_list():
    send(build_json_msg("user_list_request"))
    print("-- user list requested --")
    time.sleep(1)
    notifs = list(reversed(NOTIFICATIONS.copy()))

    for notif in notifs:
        if notif["msg_type"] == "user_list":
            print("\nActive users:")
            for user in notif["recipients"]:
                print(user)
            print()
            break
    NOTIFS_LOCK.acquire()
    NOTIFICATIONS.remove(notif)
    NOTIFS_LOCK.release()


def hack():
    user = input("Who would you like to hack? ")
    send(build_json_msg("hack", recipients=[user]))
    print("-- hacking in progress --")


def identify_user():

    def _grab_user_or_pass(user_or_pass, double_check=False):
        info = input(
            f"Enter your {'4-character ' if user_or_pass == 'passcode' else ''}{user_or_pass}: "
        )

        if double_check:
            info2 = input(
                f"Re-enter your {'4-character ' if user_or_pass == 'passcode' else ''}{user_or_pass}: "
            )
            if info != info2:
                print("Entries do not match")
                return _grab_user_or_pass(user_or_pass, double_check)

        send(info)
        return receive()["msg_body"], info

    server_msg, username = _grab_user_or_pass("username")

    """
    Possible cases:
        "new user": username available; proceed to passcode creation
        "enter passcode": username exists; user not currently active; proceed to passcode entry
        "user active": username exists; user already active; ask for new username
        "username invalid": username needs to be 4-20 characters; ask for new username
        "passcode accepted": end case; passcode accepted; proceed to program
    """

    while server_msg != "passcode accepted":

        if server_msg == "new user":
            server_msg, passcode = _grab_user_or_pass("passcode", double_check=True)

        elif server_msg == "enter passcode":
            server_msg, passcode = _grab_user_or_pass("passcode")

        elif server_msg == "user active":
            print("User already active, please choose a new username")
            server_msg, username = _grab_user_or_pass("username")

        elif server_msg == "username invalid":
            print("Username must be between 4 and 20 characters")
            server_msg, username = _grab_user_or_pass("username")

    return username, passcode


def send(msg):
    """
    This function will send a message to the server. It will first send the length of the message, then the message itself.
    :param msg: The message to be sent
    :return: None
    """
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))

    client.send(send_length)
    client.send(message)


def receive(return_type="json"):
    msg_length = client.recv(HEADER).decode(FORMAT)

    if not msg_length:
        return

    msg_length = int(msg_length)
    msg = client.recv(msg_length).decode(FORMAT)

    if return_type == "json":
        msg = json.loads(msg)

    # print(f"[SERVER] {msg}")

    return msg


def build_json_msg(
    msg_type: str,
    msg_body: str = "",
    msg_subject: str = "",
    recipients: list[str] = [],
    username: str = "",
):
    message = {
        "msg_type": msg_type,
        "msg_subject": msg_subject,
        "msg_body": msg_body,
        "recipients": recipients,
        "username": username,
    }
    return json.dumps(message)


if __name__ == "__main__":
    main()
