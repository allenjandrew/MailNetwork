from http.server import HTTPServer, BaseHTTPRequestHandler

# from socketserver import ThreadingMixIn
import time
import json
import os

TOP_API_URL = "http://127.0.0.1:8790"

DELAY = 0.0  # one second

master_dict = {}


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        global master_dict
        print(f"Request: {self.path}")

        # delay the reply from the server
        time.sleep(DELAY)

        # check to top level URL
        if self.path == "/":
            reply = "Welcome to my API"

            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(reply))

        else:
            # remove the ending '/' if found
            if self.path[-1] == "/":
                self.path = self.path[:-1]

            request = self.path[1:]  # "people/1"
            parts = request.split("/")
            # print(parts)

            if len(parts) != 2:
                reply = "hey there sucker"
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str.encode(reply))
                # self.send_error(404)
                # self.wfile.write(str.encode('Error 404 - not found'))
            else:
                command = parts[0]
                # Check for valid command
                if command != "recipes":
                    self.send_error(404)
                    # self.wfile.write(str.encode('Error 404 - not found'))
                else:
                    recipe_id = parts[1]
                    if recipe_id not in master_dict[command]:
                        self.send_error(404)
                        # self.wfile.write(str.encode('Error 404 - not found'))
                    else:
                        reply = json.dumps(master_dict[command][recipe_id])
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(str.encode(reply))


class MyServer(HTTPServer):
    pass


def main():
    global master_dict

    if not os.path.exists("recipes.json"):
        print('Error the file "recipes.json" not found')
        return

    # load dict
    with open("recipes.json") as f:
        data = f.read()

    # reconstructing the data as a dictionary
    master_dict = json.loads(data)

    # testing
    # print(type(master_dict['people1']))
    # print(master_dict['films6'])

    print(f"Recipe server waiting..... \nURL: {TOP_API_URL}")

    server = MyServer(("localhost", 8790), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
