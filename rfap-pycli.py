#!/usr/bin/env python3

from platform import platform
import colorama
import getopt
import librfap
import os
import pprint
import sys
import threading
import time
import yaml

class RfapCliApp:
    # default settings
    settings = {
            "Server": "localhost",
            "Port": 6700,
            "ColoredLS": False,
            "Debug": False
            }
    SUPPORTED_LIBRFAP_VERSIONS = ["0.3.0"]

    # app init
    def __init__(self):
        print("Welcome to rfap-pycli!")
        print(f"OS info: {platform()} with Python {sys.version}, librfap v{librfap.__version__}")
        if librfap.__version__ not in self.SUPPORTED_LIBRFAP_VERSIONS:
            print("Error: you are using an unsupported version of librfap")
            print(f"{librfap.__version__} not in {self.SUPPORTED_LIBRFAP_VERSIONS}")
            sys.exit(1)

        colorama.init()
        self.style = colorama.Style
        self.style_fg = colorama.Fore
        self.style_bg = colorama.Back

        if not os.getenv("RFAP_PYCLI_CONFIG") is None:
            self.config_file = str(os.getenv("RFAP_PYCLI_CONFIG"))
        elif not os.getenv("XDG_CONFIG_HOME") is None:
            self.config_file = os.path.join(str(os.getenv("XDG_CONFIG_HOME")), "rfap-pycli", "config.yml")
        else:
            self.config_file = os.path.expanduser("~/.config/rfap-pycli/config.yml")

        self.prompt = f"{self.style_fg.CYAN}rfap {self.style_fg.BLUE}%s{self.style.RESET_ALL} > "
        self.pwd = "/"
        self.cmd = ""
        self.args = ()

        self.configure()

        print(f"{self.style_fg.YELLOW}Connecting to {self.settings['Server']}:{self.settings['Port']}...{self.style.RESET_ALL}")
        self.client = librfap.Client(self.settings["Server"], port=self.settings["Port"])

        self.running = True
        self.time_left = 60
        self.keep_alive_thread = threading.Thread(target=self.keep_alive)
        self.socket_lock = threading.Lock()
        self.keep_alive_thread.start()
        print("Started keep-alive-thread")

        self.cmd_ping()
        self.print_success(f"Connected to {self.settings['Server']}:{self.settings['Port']}")

    # helper functions
    def configure(self):
        if os.path.exists(self.config_file):
            print(f"loading config file {self.config_file}...")
            with open(self.config_file, "r") as f:
                config = yaml.load(f.read(), Loader=yaml.SafeLoader)
                if not config is None:
                    self.settings |= config
        try:
            opts, _ = getopt.getopt(sys.argv[1:], "s:cd", ["server-address=", "--colored-ls", "--debug"])
        except getopt.GetoptError:
            self.print_error(f"invalid arguments")
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

    def getenv(self, name, default):
        if not os.getenv(name) is None:
            return os.getenv(name)
        return default

    def keep_alive(self):
        while True:
            if not self.running:
                return
            time.sleep(5)
            self.socket_lock.acquire()
            if self.time_left <= 5:
                self.client.rfap_ping()
                self.time_left = 60
            else:
                self.time_left -= 5
            self.socket_lock.release()

    def enter_cmd(self):
        inp = input(self.prompt % self.pwd).split()
        self.cmd, self.args = inp[0], tuple(inp[1:])

    def abspath(self, path: str) -> str:
        if path == "/":
            return path
        if path.startswith("/"):
            return path
        if path == ".":
            return self.pwd
        if path == "..":
            return self.parent_dir(self.pwd)

        while path.endswith("/"):
            path = path[:-1]
        _pwd = self.pwd
        while _pwd.endswith("/"):
            _pwd = self.pwd[:-1]

        if path.startswith("../"):
            return self.parent_dir(_pwd) + "/" + path[3:]
        if path.startswith("./"):
            return _pwd + "/" + path[2:]
        return _pwd + "/" + path

    def parent_dir(self, path: str) -> str:
        if path == "/":
            return "/"
        return "/" + "/".join(path.split("/")[:-1])

    def confirm(self, msg: str = "Do you really want to continue"):
        inp = input(f"{self.style_fg.YELLOW}{msg} [y/n]? {self.style.RESET_ALL}")
        if inp in ("y", "Y", "yes", "YES", "Yes"):
            return True
        return False

    def print_success(self, message: str) -> None:
        print(f"{self.style_fg.GREEN}{message}{self.style.RESET_ALL}")

    def print_error(self, message: str) -> None:
        print(f"{self.style_fg.RED}Error: {message}.{self.style.RESET_ALL}")

    # cli commands
    def cmd_cat(self):
        try:
            argument = self.abspath(self.args[0])
        except IndexError:
            self.print_error("you need to provide an argument")
            return
        self.socket_lock.acquire()
        metadata, content = self.client.rfap_file_read(argument)
        self.time_left = 60
        self.socket_lock.release()
        if metadata["ErrorCode"] != 0:
            self.print_error(f"Error: {metadata['ErrorMessage']}")
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
            argument = self.abspath(self.args[0])
        except IndexError:
            argument = "/"
        if argument == self.pwd:
            print(f"{self.style_fg.CYAN}{self.pwd}{self.style.RESET_ALL}")
            return
        self.socket_lock.acquire()
        metadata = self.client.rfap_info(argument)
        self.time_left = 60
        self.socket_lock.release()
        if metadata["ErrorCode"] != 0:
            self.print_error(f"cannot cd to '{argument}': {metadata['ErrorMessage']}")
            return
        if metadata["Type"] != "d":
            self.print_error(f"cannot cd to '{argument}': not a directory")
            return
        self.pwd = argument
        print(argument)

    def cmd_cfg(self):
        if len(self.args) == 0:
            pprint.pprint(self.settings)
            return
        try:
            key, value = self.args[0], self.args[1]
        except IndexError:
            self.print_error("you need to provide a key and a value")
            return
        if value in ("True", "true", "yes", "Yes", "enable", "Enable"):
            value = True
        if value in ("False", "false", "no", "No", "disable", "Disable"):
            value = False
        self.settings[key] = value

    def cmd_clear(self):
        if os.name == "posix":
            os.system("clear")
            return
        if os.name == "nt":
            os.system("cls")
            return
        self.print_error(f"clear command not available in {os.name} operating system")

    def cmd_copy(self):
        try:
            source = self.abspath(self.args[0])
            destin = self.abspath(self.args[1])
        except IndexError:
            self.print_error(f"you need to provide a source and a destination")
            return
        self.socket_lock.acquire()
        data = self.client.rfap_file_copy(source, destin)
        self.time_left = 60
        self.socket_lock.release()
        if data["ErrorCode"] != 0:
            self.print_error(data["ErrorMessage"])
            return
        self.print_success(f"'{self.args[0]}' copied to '{self.args[1]}'.")

    def cmd_copydir(self):
        try:
            source = self.abspath(self.args[0])
            destin = self.abspath(self.args[1])
        except IndexError:
            self.print_error(f"you need to provide a source and a destination")
            return
        self.socket_lock.acquire()
        data = self.client.rfap_directory_copy(source, destin)
        self.time_left = 60
        self.socket_lock.release()
        if data["ErrorCode"] != 0:
            self.print_error(data["ErrorMessage"])
            return
        self.print_success(f"'{self.args[0]}' copied to '{self.args[1]}'.")

    def cmd_edit(self):
        try:
            argument = self.abspath(self.args[0])
        except IndexError:
            self.print_error(f"you need to provide a file to edit")
            return
        data = []
        print("Enter the file content. Type '*EXIT' to abort. Type '*EOF' if you are done.")
        line = input(f"{self.style_fg.CYAN}| {self.style.RESET_ALL}")
        while line != "*EOF":
            if line == "*EXIT":
                self.print_error("writing to file aborted")
                return
            data.append(line)
            line = input(f"{self.style_fg.CYAN}| {self.style.RESET_ALL}")
        self.socket_lock.acquire()
        metadata = self.client.rfap_file_write(argument, "\n".join(data).encode("utf-8"))
        self.time_left = 60
        self.socket_lock.release()
        if metadata["ErrorCode"] != 0:
            self.print_error(metadata["ErrorMessage"])
            return
        self.print_success(f"'{self.args[0]}' updated.")

    def cmd_help(self):
        self.print_error("help is coming soon xD")

    def cmd_info(self):
        try:
            argument = self.abspath(self.args[0])
        except IndexError:
            argument = self.pwd
        self.socket_lock.acquire()
        metadata = self.client.rfap_info(argument)
        self.time_left = 60
        self.socket_lock.release()
        pprint.pprint(metadata)

    def cmd_ls(self):
        try:
            argument = self.abspath(self.args[0])
        except IndexError:
            argument = self.pwd
        self.socket_lock.acquire()
        metadata, files = self.client.rfap_directory_read(argument)
        self.time_left = 60
        self.socket_lock.release()
        if metadata["ErrorCode"] != 0:
            self.print_error(metadata["ErrorMessage"])
            return
        if not self.settings["ColoredLS"]:
            for f in files:
                print(f)
            return
        regular_files = []
        for f in files:
            self.socket_lock.acquire()
            m = self.client.rfap_info(argument + "/" + f)
            self.time_left = 60
            self.socket_lock.release()
            if m["Type"] == "d":
                print(f"{self.style_fg.BLUE}{f}/{self.style.RESET_ALL}")
            else:
                regular_files.append(f)
        for f in regular_files:
            print(f)

    def cmd_move(self):
        try:
            source = self.abspath(self.args[0])
            destin = self.abspath(self.args[1])
        except IndexError:
            self.print_error("you need to provide a source and a destination")
            return
        self.socket_lock.acquire()
        data = self.client.rfap_file_move(source, destin)
        self.time_left = 60
        self.socket_lock.release()
        if data["ErrorCode"] != 0:
            self.print_error(data["ErrorMessage"])
            return
        self.print_success(f"'{self.args[0]}' moved to '{self.args[1]}'.")

    def cmd_movedir(self):
        try:
            source = self.abspath(self.args[0])
            destin = self.abspath(self.args[1])
        except IndexError:
            self.print_error("you need to provide a source and a destination")
            return
        self.socket_lock.acquire()
        data = self.client.rfap_directory_move(source, destin)
        self.time_left = 60
        self.socket_lock.release()
        if data["ErrorCode"] != 0:
            self.print_error(data["ErrorMessage"])
            return
        self.print_success(f"'{self.args[0]}' moved to '{self.args[1]}'.")

    def cmd_ping(self):
        self.socket_lock.acquire()
        self.client.rfap_ping()
        self.time_left = 60
        self.socket_lock.release()
        self.print_success("sent ping")

    def cmd_rm(self):
        try:
            argument = self.abspath(self.args[0])
        except IndexError:
            self.print_error("you need to provide an argument")
            return
        self.socket_lock.acquire()
        data = self.client.rfap_file_delete(argument)
        self.time_left = 60
        self.socket_lock.release()
        if data["ErrorCode"] != 0:
            self.print_error(data["ErrorMessage"])
            return
        self.print_success(f"Deleted '{self.args[0]}'.")

    def cmd_rmdir(self):
        try:
            argument = self.abspath(self.args[0])
        except IndexError:
            self.print_error("you need to provide an argument")
            return
        self.socket_lock.acquire()
        data = self.client.rfap_directory_delete(argument)
        self.time_left = 60
        self.socket_lock.release()
        if data["ErrorCode"] != 0:
            self.print_error(data["ErrorMessage"])
            return
        self.print_success(f"Deleted '{self.args[0]}'.")

    def cmd_save(self):
        try:
            argument = self.abspath(self.args[0])
            destin = self.args[1]
        except IndexError:
            self.print_error("you need to provide a remote source and a local destination")
            return
        self.socket_lock.acquire()
        metadata, content = self.client.rfap_file_read(argument)
        self.time_left = 60
        self.socket_lock.release()
        if metadata["ErrorCode"] != 0:
            self.print_error(metadata["ErrorMessage"])
            return
        if os.path.exists(destin):
            if not self.confirm(f"Warning: '{destin}' already exists. Overwrite"):
                return
        f = open(destin, "wb")
        f.write(content)
        f.close()
        self.print_success(f"Saved '{argument}' to '{destin}'.")

    def cmd_touch(self):
        try:
            argument = self.abspath(self.args[0])
        except IndexError:
            self.print_error("you need to provide an argument")
            return
        self.socket_lock.acquire()
        data = self.client.rfap_file_create(argument)
        self.time_left = 60
        self.socket_lock.release()
        if data["ErrorCode"] == 0:
            self.print_error(data["ErrorMessage"])
            return
        self.print_success(f"Created '{argument}'.")

    def cmd_upload(self):
        try:
            argument = self.args[0]
            destin = self.abspath(self.args[1])
        except IndexError:
            self.print_error("you need to provide a local source and a remote destination")
            return
        try:
            f = open(argument, "rb")
            data = f.read()
            f.close()
        except Exception as e:
            self.print_error(f"Error reading {argument}: {e}")
            return
        self.socket_lock.acquire()
        metadata = self.client.rfap_file_write(destin, data)
        self.time_left = 60
        self.socket_lock.release()
        if metadata["ErrorCode"] != 0:
            self.print_error(metadata["ErrorMessage"])
            return
        self.print_success(f"Uploaded '{argument}' to '{destin}'.")

    # mainloop
    def run(self):
        while self.cmd not in ("exit", "quit", "disconnect", ":q"):
            try:
                match self.cmd:
                    case "cat" | "read" | "print":
                        self.cmd_cat()
                    case "cd":
                        self.cmd_cd()
                    case "cfg" | "config" | "set":
                        self.cmd_cfg()
                    case "clear" | "cls":
                        self.cmd_clear()
                    case "copy" | "cp":
                        self.cmd_copy()
                    case "copydir" | "cpdir":
                        self.cmd_copydir()
                    case "debug" | "exec":
                        if self.settings["Debug"]:
                            exec(input(f"{self.style_fg.RED}exec> {self.style.RESET_ALL}"))
                        else:
                            self.print_error("this command is only available in debug mode")
                    case "edit" | "write":
                        self.cmd_edit()
                    case "help":
                        self.cmd_help()
                    case "info":
                        self.cmd_info()
                    case "ls" | "list" | "dir":
                        self.cmd_ls()
                    case "move" | "mv" | "rename":
                        self.cmd_move()
                    case "movedir" | "mvdir":
                        self.cmd_movedir()
                    case "ping":
                        self.cmd_ping()
                    case "pwd":
                        print(self.pwd)
                    case "rm" | "remove" | "del" | "delete":
                        self.cmd_rm()
                    case "rmdir" | "deldir":
                        self.cmd_rmdir()
                    case "save" | "download" | "dl":
                        self.cmd_save()
                    case "touch" | "create":
                        self.cmd_touch()
                    case "upload":
                        self.cmd_upload()
                    case "":
                        pass
                    case _:
                        self.print_error(f"{self.cmd}: command not found, type 'help' for help")
                self.enter_cmd()
            except KeyboardInterrupt:
                break

        print(f"{self.style_fg.YELLOW}Disconnecting, please wait...{self.style.RESET_ALL}")
        self.running = False
        self.keep_alive_thread.join()
        self.client.rfap_disconnect()
        self.time_left = 60
        self.print_success("done.")

# IFMAIN
if __name__ == "__main__":
    app = RfapCliApp()
    app.run()

