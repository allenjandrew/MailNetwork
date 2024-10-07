"""
Course: CSE 251 
Lesson: L02 Prove
File:   prove.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- Each API call must only retrieve one piece of information
- You are not allowed to use any other modules/packages except for the ones used
  in this assignment.
- Run the server.py program from a terminal/console program.  Simply type
  "python server.py"
- The only "fixed" or hard coded URL that you can use is TOP_API_URL.  Use this
  URL to retrieve other URLs that you can use to retrieve information from the
  server.
- You need to match the output outlined in the description of the assignment.
  Note that the names are sorted.
- You are required to use a threaded class (inherited from threading.Thread) for
  this assignment.  This object will make the API calls to the server. You can
  define your class within this Python file (ie., no need to have a separate
  file for the class)
- Do not add any global variables except for the ones included in this program.

The call to TOP_API_URL will return the following Dictionary(JSON).  Do NOT have
this dictionary hard coded - use the API call to get this.  Then you can use
this dictionary to make other API calls for data.

{
   "people": "http://127.0.0.1:8790/people/", 
   "planets": "http://127.0.0.1:8790/planets/", 
   "films": "http://127.0.0.1:8790/films/",
   "species": "http://127.0.0.1:8790/species/", 
   "vehicles": "http://127.0.0.1:8790/vehicles/", 
   "starships": "http://127.0.0.1:8790/starships/"
}
"""

from datetime import datetime, timedelta
import requests
import json
import threading

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = "http://127.0.0.1:8790"

# Global Variables
call_count = 0


# TODO Add your threaded class definition here
class Request_thread(threading.Thread):

    # Constructor
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.data = {}

    # On Start
    def run(self):
        global call_count
        response = requests.get(self.url)
        # self.sc = response.status_code
        if response.status_code == 200:  # if this is a valid response:
            self.data = response.json()
            # print(self.data)
        call_count += 1


# TODO Add any functions you need here
def print_progress(list, data):
    progress = 100 * len(list) / len(data)
    print(("\b\b\b\b", "\b\b\b")[progress < 10], f"{progress:.0f}%", end="", flush=True)


def get_names(dataset, group):
    names = []
    threads = []
    for item in dataset[group]:
        threads.append(Request_thread(item))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for t in threads:
        names.append(t.data["name"])
    print(group.capitalize() + " loaded")
    return names


def main():
    log = Log(show_terminal=True)
    log.start_timer("Starting to retrieve data from the server\n")

    # TODO Retrieve Top API urls
    t1 = Request_thread(TOP_API_URL)
    t1.start()
    t1.join()
    # print(t1.data)

    # TODO Retrieve Details on film 6
    t2 = Request_thread(f"{t1.data['films']}6")
    t2.start()
    t2.join()
    data = t2.data
    # print(t2.url)
    # print(t2.sc)
    # print(t2.data)

    char_names = get_names(data, "characters")
    plan_names = get_names(data, "planets")
    ship_names = get_names(data, "starships")
    vehc_names = get_names(data, "vehicles")
    spec_names = get_names(data, "species")

    # TODO Display results
    print(
        f"\n\nTitle: {data['title']}\nDirector: {data['director']}\nProducer: {data['producer']}\nReleased: {data['release_date']}"
    )

    print(f"\nCharacters: {len(char_names)}")
    print(*char_names, sep=", ")

    print(f"\nPlanets: {len(plan_names)}")
    print(*plan_names, sep=", ")

    print(f"\nStarships: {len(ship_names)}")
    print(*ship_names, sep=", ")

    print(f"\nVehicles: {len(vehc_names)}")
    print(*vehc_names, sep=", ")

    print(f"\nSpecies: {len(spec_names)}")
    print(*spec_names, sep=", ")

    print()
    log.stop_timer("\nTotal Time To complete")
    log.write(f"There were {call_count} calls to the server\n")


if __name__ == "__main__":
    main()
