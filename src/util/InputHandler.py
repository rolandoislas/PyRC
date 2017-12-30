from threading import Thread

from src.data.args import Args
from src.data.cmd import *


class InputHandler:
    def __init__(self, irc):
        self.running = False
        self.irc = irc
        self.listen_thread = Thread(target=self._listen)
        self.listen_thread.setDaemon(True)
        self.listen_thread.setName("INPUT")

    def listen(self):
        """
        Start the listen thread
        :return: None
        """
        self.running = True
        self.listen_thread.start()

    def _listen(self):
        """
        Listen for and handle user input
        FIXME This implementation is horrible for input, but Tk or ncurses is not worth it
        :return: None
        """
        while self.is_running():
            input_string = input("> ")
            # Handle command
            if input_string.startswith("/"):
                cmd_split = input_string.replace("/", "", 1).split(" ")
                if len(cmd_split) > 0:
                    if cmd_split[0].upper() == "JOIN":
                        if len(cmd_split) > 1:
                            self.irc.set_channel(cmd_split[1])
                    elif cmd_split[0].upper() == "PART":
                        self.irc.set_channel()

            # Chat message
            else:
                self.irc.print_message("(%s)" % Args.args.user_name, input_string)
                self.irc.cmd(PRIVMSG, self.irc.get_channel(), input_string)

    def is_running(self):
        """
        Check if the listen thread is running
        :return: running
        """
        return self.running

    def stop(self):
        """
        Stop the listen thread
        :return: None
        """
        self.running = False
