import logging
import os
import sys

from tambo import Transport
import chacractl
from chacractl.api import binaries, repos, exists, projects
from chacractl.decorators import catches
from chacractl import log, util


class ChacraCtl(object):
    _help = """
chacractl: A utility to interact with a Chacra (binary HTTP API) service.

Version: %s

Global Options:
--log, --logging    Set the level of logging. Acceptable values:
                    debug, warning, error, critical

Sub Commands:
%s

    """

    mapper = {
        'binary': binaries.Binary,
        'project': projects.Project,
        'repo': repos.Repo,
        'exists': exists.Exists,
    }

    def __init__(self, argv=None, parse=True):
        if argv is None:
            argv = sys.argv
        if parse:
            self.main(argv)

    def help(self):
        sub_help = '\n'.join(['%-19s %s' % (
            sub.__name__.lower(), getattr(sub, 'help_menu', ''))
            for sub in self.mapper.values()])
        return self._help % (chacractl.__version__, sub_help)

    def api_credentials(self):
        util.ensure_default_config()
        user, key = os.environ.get('CHACRA_USER'), os.environ.get('CHACRA_KEY')
        if not user or not key:
            # check for the config file
            conf_module = util.load_config()
            user, key = conf_module.user, conf_module.key
        chacractl.config['credentials'] = (user, key)
        chacractl.config['url'] = conf_module.url
        chacractl.config['ssl_verify'] = getattr(conf_module, 'ssl_verify', True)

    @catches((RuntimeError, KeyboardInterrupt))
    def main(self, argv):
        # Console Logger
        sh = logging.StreamHandler()
        sh.setFormatter(log.color_format())
        sh.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(sh)

        self.api_credentials()

        # TODO: Need to implement `--filename` and make it available
        options = [['--log', '--logging']]
        parser = Transport(argv, mapper=self.mapper,
                           options=options, check_help=False,
                           check_version=False)
        parser.parse_args()
        chacractl.config['verbosity'] = parser.get('--log', 'info')
        parser.catch_help = self.help()
        parser.catch_version = chacractl.__version__
        parser.mapper = self.mapper
        if len(argv) <= 1:
            return parser.print_help()
        parser.dispatch()
        parser.catches_help()
        parser.catches_version()
