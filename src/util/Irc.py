import codecs
import socket

import re
from threading import Thread

from src.data.args import Args
from src.data.cmd import *
from src.util.logger import Logger


class Irc:
    def __init__(self):
        """
        Class for handling IRC functions
        """
        self.running = False
        self.channel = None
        params_regex = "(\s(?:(?::(.*))|(?:([^\s]+))))"
        self.params_regex = re.compile(params_regex)
        self.message_regex = re.compile(
            "^(?::([^!@\s]+)(?:!([^@\s]+))?(?:@([^\s]+))?\s)?([A-Za-z0-9]+)($PARAMS+)(?:\r?\n?)".replace("$PARAMS",
                                                                                                         params_regex))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_thread = Thread(target=self._listen)
        self.listen_thread.setDaemon(True)
        self.listen_thread.setName("IRC")

    def connect(self):
        """
        Start connecting to the IRC server
        :return: None
        """
        self.socket.connect((Args.args.server, 6667))
        Logger.info("Connected to %s", Args.args.server)
        self.cmd(PASS, Args.args.password)
        self.cmd(NICK, Args.args.user_name)

    def listen(self):
        """
        Start the listen thread
        :return: None
        """
        self.running = True
        self.listen_thread.start()

    def _listen(self):
        """
        Continuously listen for data from the IRC server and handle when appropriate
        :return: None
        """
        data = ""
        while self.is_running():
            try:
                data += codecs.decode(self.socket.recv(2048))
            except (ValueError, OSError) as e:
                Logger.exception(e)
                continue
            split = data.splitlines(True)
            last_val = split[len(split) - 1]
            data = ""
            if not last_val.endswith("\n"):
                data = last_val
                del split[len(split) - 1]
            for message in split:
                Logger.verbose("MESSAGE:" + message)
                message_parsed = self.parse_message(message)
                if message_parsed:
                    self.handle_message(message_parsed)

    def parse_message(self, message_string):
        """
        Parse an IRC message
        :param message_string: plaintext message string
        :return: Tuple of matched groups or None if there was no match
        """
        match = self.message_regex.match(message_string)
        if not match:
            return None
        Logger.verbose("========================= COMMAND =========================")
        groups = match.groups()
        for group in groups:
            Logger.verbose(group)
        message = {
            "server_name": groups[0],
            "nick": groups[0],
            "user": groups[1],
            "host": groups[2],
            "command": groups[3],
            "params": self.parse_params(groups[4])
        }
        return message

    def handle_message(self, message):
        """
        Handle an IRC message
        :param message: regex groups tuple
        :return: None
        """
        Logger.extra(message)
        if message["command"] == PING:
            self.cmd(PONG, message["params"][0])
        elif message["command"] == PRIVMSG:
            self.print_message(message["nick"], message["params"][1])
        elif MOTD_TWITCH.match(message["command"]) or message["command"] == MOTD_START_D or \
                message["command"] == MOTD_D or message["command"] == MOTD_END_D:
            self.print_message("[%s]" % message["nick"], message["params"][1])
        elif message["command"] == JOIN:
            Logger.info("Joined %s", message["params"][0])
        elif message["command"] == PART:
            Logger.info("Departed %s", message["params"][0])

    def parse_params(self, param_string):
        """
        Parse params into an ordered list
        :param param_string: param string starting with a space
        :return: list
        """
        params = []
        matches = self.params_regex.finditer(param_string)
        if not matches:
            return None
        for match in matches:
            groups = match.groups()
            if groups[1]:
                params.append(groups[1])
            elif groups[2]:
                params.insert(0, groups[2])
        return params

    def cmd(self, cmd, *args):
        """
        Send a command to the server
        :param cmd: command
        :param args: parameters
        :return: None
        """
        formatted_args = ""
        for arg_index in range(len(args)):
            if arg_index == len(args) - 1:
                formatted_args += ":" + args[arg_index]
            else:
                formatted_args += args[arg_index] + " "
        try:
            self.socket.sendall(codecs.encode("%s %s\r\n" % (cmd, formatted_args)))
        except OSError as e:
            Logger.exception(e)
            self.connect()

    def print_message(self, user_name, message):
        """
        Print a user message from a user
        :param user_name: name of user
        :param message: message
        :return: None
        """
        print("%s: %s" % (user_name, message))

    def is_running(self):
        """
        Getter
        :return: running
        """
        return self.running

    def stop(self):
        """
        Stop the listen thread
        :return: None
        """
        self.running = False

    def get_channel(self):
        """
        Getter for the current channel
        :return: channel
        """
        return self.channel

    def set_channel(self, channel=None):
        """
        Leave any previous channel and join the new one
        :param channel: channel
        """
        if self.channel:
            self.cmd(PART, self.channel)
        self.channel = channel
        if self.channel:
            self.cmd(JOIN, self.channel)
