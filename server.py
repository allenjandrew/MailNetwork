import socket
import threading
import json

if True:
    # A header will be sent first to determine the length of the message
    HEADER = 16
    # This is the port that the server will be listening on
    PORT = 50505
    # This is the IP address of the server
    SERVER = socket.gethostbyname(socket.gethostname())
    # This is the address of the server - a tuple of the server and port
    ADDR = (SERVER, PORT)
    # This is the format that the server will be using
    FORMAT = "utf-8"
    # This is the message that will be sent so the server knows to disconnect
    DISCONNECT_MESSAGE = "!DISCONNECT"

    MASTER_USER_DICT = {}


def main():
    # print(SERVER)
    # print(socket.gethostname())

    # Create a socket object. The first parameter is the address family. AF_INET is the address family for IPv4. The second parameter is the socket type. SOCK_STREAM means that data will be read in chunks.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set the socket options. The first parameter is the level of the socket. The second parameter is the socket option. The third parameter is the value of the socket option. This will allow the server to reuse the address instead of having to wait a minute for the socket to timeout.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the server to the address. The bind method takes in a tuple of the server and port
    server.bind(ADDR)

    print("[STARTING] server is starting...")
    start(server)


def start(server):
    server.listen()

    print(f"[LISTENING] Server is listening on {SERVER}")

    while True:
        conn, addr = server.accept()
        runner = threading.Thread(target=handle_client, args=(conn, addr))
        runner.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def handle_client(conn, addr):
    """
    This function will handle the connection between the client and the server. It will receive messages from the client and print them out. If the message is the disconnect message, the connection will be closed.
    :param conn: The connection object
    :param addr: The address of the client
    :return: None
    """
    global MASTER_USER_DICT

    username = register_user(conn, addr)

    print(f"[NEW CONNECTION] {username} connected.")

    connected = True
    while connected:
        msg = receive(conn)
        send(conn, build_json_msg("info", msg_body="Message received"))

        if msg["msg_type"] == DISCONNECT_MESSAGE:
            connected = False
            MASTER_USER_DICT[username]["active"] = False
            send(conn, build_json_msg(DISCONNECT_MESSAGE))

        else:
            switcher = {
                "email": handle_email_or_text,
                "text": handle_email_or_text,
                "announcement": handle_announcement,
                "hack": get_hacked,
                "user_list_request": handle_user_list_request,
            }
            switcher.get(msg["msg_type"], invalid_message)(conn, msg)

    conn.close()


def send(conn, message):
    msg = message.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))

    conn.send(send_length)
    conn.send(msg)


def invalid_message(conn, message):
    send(
        conn,
        build_json_msg(
            "info", msg_body="Error: Invalid Message Type: " + message["msg_type"]
        ),
    )


def register_user(conn, addr):

    username = receive(conn, return_type="string")

    """
    Possible cases:
        "new user": username available; proceed to passcode creation
        "enter passcode": username exists; user not currently active; proceed to passcode entry
        "user active": username exists; user already active; ask for new username
        "username invalid": username needs to be 4-20 characters; ask for new username
        "passcode accepted": end case; passcode accepted; proceed to program
    """
    done = False
    while not done:

        if len(username) not in range(4, 21):
            send(conn, build_json_msg("info", msg_body="username invalid"))
            username = receive(conn, return_type="string")

        elif username in MASTER_USER_DICT.keys():

            if MASTER_USER_DICT[username]["active"]:
                send(conn, build_json_msg("info", msg_body="user active"))
                username = receive(conn, return_type="string")

            else:
                send(conn, build_json_msg("info", msg_body="enter passcode"))
                passcode = receive(conn, return_type="string")

                if passcode == MASTER_USER_DICT[username]["passcode"]:
                    done = True

        else:
            send(conn, build_json_msg("info", msg_body="new user"))
            passcode = receive(conn, return_type="string")
            done = True

    send(conn, build_json_msg("info", msg_body="passcode accepted"))
    _update_master_user_list(username, conn, addr, True, passcode)
    return username


def _update_master_user_list(username: str, conn, addr, active: bool, passcode: str):
    global MASTER_USER_DICT
    MASTER_USER_DICT[username] = {
        "conn": conn,
        "addr": addr,
        "active": active,
        "passcode": passcode,
    }


def receive(conn, return_type="json"):
    msg_length = conn.recv(HEADER).decode(FORMAT)

    if not msg_length:
        return

    msg_length = int(msg_length)
    msg = conn.recv(msg_length).decode(FORMAT)

    if return_type == "json":
        msg = json.loads(msg)

    return msg


def handle_email_or_text(conn, message):
    for recipient in message["recipients"]:
        if recipient not in MASTER_USER_DICT.keys():
            send(
                conn,
                build_json_msg(
                    "info", msg_body="Error: Recipient not found: " + recipient
                ),
            )
        elif not MASTER_USER_DICT[recipient]["active"]:
            send(
                conn,
                build_json_msg(
                    "info", msg_body="Error: Recipient not active: " + recipient
                ),
            )
        else:
            send(MASTER_USER_DICT[recipient]["conn"], json.dumps(message))


def handle_announcement(conn, message):
    for recipient in MASTER_USER_DICT.keys():
        if MASTER_USER_DICT[recipient]["active"]:
            send(MASTER_USER_DICT[recipient]["conn"], json.dumps(message))


def get_hacked(conn, message):
    for recipient in message["recipients"]:
        if recipient not in MASTER_USER_DICT.keys():
            continue
        elif not MASTER_USER_DICT[recipient]["active"]:
            continue
        else:
            send(
                MASTER_USER_DICT[recipient]["conn"],
                build_json_msg(
                    "hack",
                    msg_subject="You've been hacked!",
                    msg_body="Please follow this link to recover your work: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    recipients=[recipient],
                ),
            )


def handle_user_list_request(conn, message):
    users = list(MASTER_USER_DICT.keys())
    send(conn, build_json_msg("user_list", recipients=users))


def build_json_msg(
    msg_type: str, msg_body: str = "", msg_subject: str = "", recipients: list[str] = []
):
    message = {
        "msg_type": msg_type,
        "msg_subject": msg_subject,
        "msg_body": msg_body,
        "recipients": recipients,
    }
    return json.dumps(message)


if __name__ == "__main__":
    main()
