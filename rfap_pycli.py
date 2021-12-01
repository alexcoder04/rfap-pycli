#!/usr/bin/env python3

import librfap
import getopt
import sys

PROMPT = "rfap> "

if __name__ == "__main__":
    print("Welcome to rfap-pycli!")
    server_address = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:", ["server-address="])
    except getopt.GetoptError:
        print(sys.argv[0], "-s server_address")
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-s", "--server-address"):
            server_address = arg
    if server_address is None:
        server_address = input("server address: ")

    print("Connecting to", server_address)
    client = librfap.Client(server_address)

    command = input(PROMPT)
    while command not in ("exit", "quit", ":q"):
        command = input(PROMPT)

    print("disconnecting...")
    client.rfap_disconnect()
    print("done.")

