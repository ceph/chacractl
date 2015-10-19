import chacractl

class Repo(object):

    help_menu = "recreate, delete, or updaterepositories"

    def __init__(self, argv):
        self.argv = argv

    def main(self):
        print chacractl.config
        pass

