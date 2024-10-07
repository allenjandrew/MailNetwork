## Overview

**Project Title**: Mail Network

**Project Description**:
A simple Python socket server that connects clients over a network. Clients can send messages back and forth.

**Project Goals**:
The server should allow email, texts, and announcements, as well as see other active users.

## Instructions for Build and Use

Steps to build and/or run the software:

1. Run server.py in a terminal.
2. The server will tell you on which ip address it's listening. Make sure the other clients have the same ip address in the global SERVER variable.
3. From any computer on the same wifi network, run client.py.
4. Multiple clients can connect at the same time.

Instructions for using the software:

1. The first thing the client program will ask for is your username. If the server hasn't seen your username before, it'll ask you to create a password, otherwise you'll just log in with the password you set before.
2. There are multiple things you can do from the main menu. You can send an email (to multiple people with a subject and body), text (to one person, with only a body), or announcement (to all users with a subject and body). You can also check your notifications, ask the server for a list of active users, or even send an anonymous malicious payload (rick roll) to another user.
3. When you're finished, don't forget to disconnect. If you don't, the server will think your profile is still active, and you won't be able to log in with your username again.

## Development Environment

To recreate the development environment, you need the following software and/or libraries with the specified versions:

- VS Code or your favorite IDE
- Python - I'm running 3.10.1
- Libraries: socket, threading, json, time

## Useful Websites to Learn More

I found these websites useful in developing this software:

- [A YouTube networking basics course](https://www.youtube.com/watch?v=0-MldfyhIuo) by Vinsloev Academy
- [Python Socket Programming Tutorial](https://www.youtube.com/watch?v=3QiPPX-KeSc) by Tech With Tim
- [Another socket programming guide](https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python) on datacamp.com
- [Another really helpful video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
- [The socket documentation](https://docs.python.org/3.6/library/socketserver.html)

## Future Work

The following items I plan to fix, improve, and/or add to this project in the future:

- [ ] Running on public internet, not just local wifi
- [ ] More error checking
- [ ] I'd like to make this web-based, not terminal-based - so I can have buttons, widgets, etc
- [ ] Keep chat / email history
- [ ] Allow messages to a user even while they're not active - they'll receive them later
