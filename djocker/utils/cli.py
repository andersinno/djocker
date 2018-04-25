import argparse
import sys


class Command:
    def __init__(self):
        self.argv = sys.argv
        self.args = self.get_args()

    def get_args(self):
        parser = argparse.ArgumentParser(description=getattr(self, 'description', ''))
        self.add_arguments(parser)
        return parser.parse_args()

    def add_arguments(self, parser):
        pass

    def handle(self):
        raise NotImplementedError()


def run_command(cmd):
    cmd().handle()
