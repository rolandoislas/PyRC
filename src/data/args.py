import argparse

from src.data import constants
from src.util.logger import Logger


class Args:
    args = None

    def __init__(self):
        pass

    @staticmethod
    def parse_args():
        arg_parser = argparse.ArgumentParser(description="%s Twitch IRC client" % constants.NAME)
        arg_parser.add_argument("user_name", type=str, help="Twitch user name", default=None)
        arg_parser.add_argument("password", type=str, help="Twitch Oauth token/password", default=None)
        arg_parser.add_argument("-server", type=str, help="Server to use for connecting",
                                default=constants.TWITCH_IRC_SERVER)
        arg_parser.add_argument("-log", type=str, help="Log level: INFO DEBUG EXTRA FINER VERBOSE",
                                default=Logger.INFO)
        arg_parser.add_argument("--save", action="store_const", const=True, default=False,
                                help="Save the token")
        Args.args = arg_parser.parse_args()
