#!/usr/bin/env python3

import librfap
import getopt
import sys

PROMPT = "rfap> "

def enter_command():
    inp = input(PROMPT).split()
    return inp[0], inp[1:]

def command_cd(oldpwd):
    if args[0] == "..":
        if oldpwd == "/":
            print(oldpwd)
            return "/"
        pwd = "/" + "/".join(oldpwd.split("/")[:-1])
    else:
        pwd = oldpwd
        while pwd.endswith("/"):
            pwd = pwd[:-1]
        pwd = pwd + "/" + args[0]
    metadata = client.rfap_info(pwd)
    if metadata["ErrorCode"] != 0:
        print(f"cannot cd to '{pwd}': {metadata['ErrorMessage']}")
        pwd = oldpwd
    else:
        if metadata["Type"] != "d":
            print(f"cannot cd to '{pwd}': not a directory")
            pwd = oldpwd
        else:
            print(pwd)
    return pwd

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

    pwd = "/"

    command, args = enter_command()
    while command not in ("exit", "quit", ":q"):
        if command in ("help"):
            print("help is coming soon xD")
        elif command in ("pwd"):
            print(pwd)
        elif command in ("cd"):
            pwd = command_cd(pwd)
        elif command in ("ls", "list", "dir"):
            metadata, files = client.rfap_directory_read(pwd)
            if metadata["ErrorCode"] != 0:
                print("Error:", metadata["ErrorMessage"])
            else:
                for f in files:
                    print(f)
        else:
            print("type 'help' for help")
        command, args = enter_command()

    print("disconnecting...")
    client.rfap_disconnect()
    print("done.")

