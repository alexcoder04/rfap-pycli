#!/usr/bin/env python3

import librfap
import colorama
import pprint
import getopt
import sys
import os

class RfapCliApp:
    # default settings
    settings = {
            "Server": "localhost",
            "Port": 6700,
            "ColoredLS": False,
            "Debug": False
            }

    # app init
    def __init__(self):
        print("Welcome to rfap-pycli!")

        colorama.init()
        self.style = colorama.Style
        self.style_fg = colorama.Fore
        self.style_bg = colorama.Back

        self.prompt = f"{self.style_fg.CYAN}rfap> {self.style.RESET_ALL}"
        self.pwd = "/"
        self.cmd = ""
        self.args = ()

        self.configure()

        print(f"{self.style_fg.YELLOW}Connecting to {self.settings['Server']}:{self.settings['Port']}...{self.style.RESET_ALL}")
        self.client = librfap.Client(self.settings["Server"], port=self.settings["Port"])
        self.cmd_ping()
        print(f"{self.style_fg.GREEN}Connected to {self.settings['Server']}:{self.settings['Port']}{self.style.RESET_ALL}")

    # helper functions
    def configure(self):
        try:
            opts, _ = getopt.getopt(sys.argv[1:], "s:cd", ["server-address=", "--colored-ls", "--debug"])
        except getopt.GetoptError:
            print(f"{self.style_fg.RED}Error: invalid arguments{self.style.RESET_ALL}")
            print("Usage:", sys.argv[0], "[-d] [-c] [-s server_address]")
            sys.exit(1)
        for opt, arg in opts:
            if opt in ("-s", "--server-address"):
                self.settings["Server"] = arg
                continue
            if opt in ("-c", "--colored-ls"):
                self.settings["ColoredLS"] = True
                continue
            if opt in ("-d", "--debug"):
                self.settings["Debug"] = True

    def enter_cmd(self):
        inp = input(self.prompt).split()
        self.cmd, self.args = inp[0], tuple(inp[1:])

    def abspath(self, path: str, pwd: str) -> str:
        if path == "/":
            return path
        if path.startswith("/"):
            return path
        if path == ".":
            return pwd
        if path == "..":
            return self.parent_dir(pwd)

        while path.endswith("/"):
            path = path[:-1]
        while pwd.endswith("/"):
            pwd = pwd[:-1]

        if path.startswith("../"):
            return self.parent_dir(pwd) + "/" + path[3:]
        if path.startswith("./"):
            return pwd + "/" + path[2:]
        return pwd + "/" + path

    def parent_dir(self, path: str) -> str:
        if path == "/":
            return "/"
        return "/" + "/".join(path.split("/")[:-1])

    # cli commands
    def cmd_cat(self):
        try:
            argument = self.abspath(self.args[0], self.pwd)
        except IndexError:
            print(f"{self.style_fg.RED}Error: you need to provide an argument{self.style.RESET_ALL}")
            return
        metadata, content = self.client.rfap_file_read(argument)
        if metadata["ErrorCode"] != 0:
            print(f"{self.style_fg.RED}Error: {metadata['ErrorMessage']}{self.style.RESET_ALL}")
            return
        if not metadata["FileType"].startswith("text/"):
            print(f"{self.style_fg.MAGENTA}{argument}: binary file ({metadata['FileType']}), not shown.{self.style.RESET_ALL}")
            return
        content_string = content.decode("utf-8")
        if not content_string.endswith("\n"):
            content_string += f"{self.style_fg.BLACK}{self.style_bg.WHITE}%{self.style.RESET_ALL}\n"
        sys.stdout.write(content_string)

    def cmd_cd(self):
        try:
            argument = self.abspath(self.args[0], self.pwd)
        except IndexError:
            argument = "/"
        if argument == self.pwd:
            print(f"{self.style_fg.CYAN}{self.pwd}{self.style.RESET_ALL}")
            return
        metadata = self.client.rfap_info(argument)
        if metadata["ErrorCode"] != 0:
            print(f"{self.style_fg.RED}cannot cd to '{argument}': {metadata['ErrorMessage']}{self.style.RESET_ALL}")
            return
        if metadata["Type"] != "d":
            print(f"{self.style_fg.RED}cannot cd to '{argument}': not a directory{self.style.RESET_ALL}")
            return
        self.pwd = argument
        print(argument)

    def cmd_clear(self):
        if os.name == "posix":
            os.system("clear")
            return
        if os.name == "nt":
            os.system("cls")
            return
        print(f"{Fore.RED}Error: clear command not available in {os.name} operating system.{Style.RESET_ALL}")

    def cmd_help(self):
        print(f"{self.style_fg.RED}help is coming soon xD{self.style.RESET_ALL}")

    def cmd_info(self):
        try:
            argument = self.abspath(self.args[0], self.pwd)
        except IndexError:
            argument = self.pwd
        metadata = self.client.rfap_info(argument)
        pprint.pprint(metadata)

    def cmd_ls(self):
        try:
            argument = self.abspath(self.args[0], self.pwd)
        except IndexError:
            argument = self.pwd
        metadata, files = self.client.rfap_directory_read(argument)
        if metadata["ErrorCode"] != 0:
            print(f"{self.style_fg.RED}Error: {metadata['ErrorMessage']}{self.style.RESET_ALL}")
            return
        if not self.settings["ColoredLS"]:
            for f in files:
                print(f)
            return
        regular_files = []
        for f in files:
            m = self.client.rfap_info(argument + "/" + f)
            if m["Type"] == "d":
                print(f"{self.style_fg.BLUE}{f}/{self.style.RESET_ALL}")
            else:
                regular_files.append(f)
        for f in regular_files:
            print(f)

    def cmd_ping(self):
        self.client.rfap_ping()
        print(f"{self.style_fg.GREEN}sent ping{self.style.RESET_ALL}")

    # mainloop
    def run(self):
        self.enter_cmd()
        while self.cmd not in ("exit", "quit", ":q"):
            match self.cmd:
                case "cat" | "read" | "print":
                    self.cmd_cat()
                case "cd":
                    self.cmd_cd()
                case "clear" | "cls":
                    self.cmd_clear()
                case "debug" | "exec":
                    if self.settings["Debug"]:
                        exec(input(f"{self.style_fg.RED}exec> {self.style.RESET_ALL}"))
                    else:
                        print(f"{self.style_fg.RED}Error: this command is only available in debug mode.{self.style.RESET_ALL}")
                case "help":
                    self.cmd_help()
                case "info":
                    self.cmd_info()
                case "ls" | "list" | "dir":
                    self.cmd_ls()
                case "ping":
                    self.cmd_ping()
                case "pwd":
                    print(self.pwd)
                case _:
                    print(f"{self.style_fg.RED}{self.cmd}: command not found, type 'help' for help{self.style.RESET_ALL}")
            self.enter_cmd()

        print(f"{self.style_fg.YELLOW}Disconnecting...{self.style.RESET_ALL}")
        self.client.rfap_disconnect()
        print(f"{self.style_fg.GREEN}done.{self.style.RESET_ALL}")

# IFMAIN
if __name__ == "__main__":
    app = RfapCliApp()
    app.run()

