#!/usr/bin/env python3

import librfap
import colorama
from colorama import Fore, Back, Style
import getopt
import sys

PROMPT = Fore.CYAN + "rfap> " + Style.RESET_ALL
COLORED_LS = False

def enter_command():
    inp = input(PROMPT).split()
    return inp[0], inp[1:]

def abspath(path: str, pwd: str) -> str:
    if path.startswith("/"):
        return path
    if path == ".":
        return pwd
    if path == "..":
        return parent_dir(pwd)

    while path.endswith("/"):
        path = path[:-1]
    while pwd.endswith("/"):
        pwd = pwd[:-1]

    if path.startswith("../"):
        return parent_dir(pwd) + "/" + path[3:]
    if path.startswith("./"):
        return pwd + "/" + path[2:]
    return pwd + "/" + path

def parent_dir(path: str) -> str:
    if path == "/":
        return "/"
    return "/" + "/".join(path.split("/")[:-1])

def command_cd(oldpwd: str, args: list) -> str:
    try:
        argument = abspath(args[0], oldpwd)
    except IndexError:
        argument = "/"
    if argument == oldpwd:
        print(Fore.GREEN + oldpwd + Style.RESET_ALL)
        return oldpwd
    metadata = client.rfap_info(argument)
    if metadata["ErrorCode"] != 0:
        print(f"{Fore.RED}cannot cd to '{argument}': {metadata['ErrorMessage']}{Style.RESET_ALL}")
        argument = oldpwd
    else:
        if metadata["Type"] != "d":
            print(f"{Fore.RED}cannot cd to '{argument}': not a directory{Style.RESET_ALL}")
            argument = oldpwd
        else:
            print(argument)
    return argument

def command_read_directory(client: librfap.Client, pwd: str, args: list) -> None:
    global COLORED_LS
    try:
        argument = abspath(args[0], pwd)
    except IndexError:
        argument = pwd
    metadata, files = client.rfap_directory_read(argument)
    if metadata["ErrorCode"] != 0:
        print(f"{Fore.RED}Error: {metadata['ErrorMessage']}{Style.RESET_ALL}")
        return
    if not COLORED_LS:
        for f in files:
            print(f)
        return
    regular_files = []
    for f in files:
        m = client.rfap_info(argument + "/" + f)
        if m["Type"] == "d":
            print(Fore.BLUE + f + Style.RESET_ALL)
        else:
            regular_files.append(f)
    for f in regular_files:
        print(f)

def command_read_file(client: librfap.Client, pwd: str, args: list) -> None:
    try:
        argument = abspath(args[0], pwd)
    except IndexError:
        argument = pwd
    metadata, content = client.rfap_file_read(argument)
    if metadata["ErrorCode"] != 0:
        print(f"{Fore.RED}Error: {metadata['ErrorMessage']}{Style.RESET_ALL}")
    else:
        if not metadata["FileType"].startswith("text/"):
            print(Fore.MAGENTA + "Binary file (" + metadata["FileType"] + "), not shown" + Style.RESET_ALL)
            return
        content_string = content.decode("utf-8")
        if not content_string.endswith("\n"):
            content_string += Fore.BLACK + Back.WHITE + "%" + Style.RESET_ALL + "\n"
        sys.stdout.write(content_string)

def command_ping(client: librfap.Client) -> None:
    client.rfap_ping()
    print(Fore.GREEN + "sent ping" + Style.RESET_ALL)

def command_info(client: librfap.Client, pwd: str, args: list) -> None:
    try:
        argument = abspath(args[0], pwd)
    except IndexError:
        argument = pwd
    metadata = client.rfap_info(argument)
    print(metadata)

if __name__ == "__main__":
    print("Welcome to rfap-pycli!")
    colorama.init()
    server_address = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:c", ["server-address=", "--colored-ls"])
    except getopt.GetoptError:
        print(sys.argv[0], "-s server_address")
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-s", "--server-address"):
            server_address = arg
            continue
        if opt in ("-c", "--colored-ls"):
            COLORED_LS = True
    if server_address is None:
        server_address = input("server address: ")

    print(Fore.YELLOW + "Connecting to", server_address + "..." + Style.RESET_ALL)
    client = librfap.Client(server_address)
    command_ping(client)
    print(Fore.GREEN + "Connected successfully" + Style.RESET_ALL)

    pwd = "/"

    command, args = enter_command()
    while command not in ("exit", "quit", ":q"):
        if command == "help":
            print(Fore.RED + "help is coming soon xD" + Style.RESET_ALL)
        elif command == "pwd":
            print(pwd)
        elif command == "cd":
            pwd = command_cd(pwd, args)
        elif command in ("ls", "list", "dir"):
            command_read_directory(client, pwd, args)
        elif command == "info":
            command_info(client, pwd, args)
        elif command == "ping":
            command_ping(client)
        elif command in ("cat", "read", "print"):
            command_read_file(client, pwd, args)
        else:
            print(Fore.RED + command  + ": unknown command, type 'help' for help" + Style.RESET_ALL)
        command, args = enter_command()

    print(Fore.YELLOW + "disconnecting..." + Style.RESET_ALL)
    client.rfap_disconnect()
    print(Fore.GREEN + "done." + Style.RESET_ALL)

