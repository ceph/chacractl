import logging
import chacractl


logger = logging.getLogger(__name__)


class Repo(object):

    help_menu = "recreate, delete, or updaterepositories"

    def __init__(self, argv):
        self.argv = argv

    def main(self):
        raise RuntimeError('repo subcommand is not yet implemented')
