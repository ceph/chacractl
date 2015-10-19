import logging
import sys
from urlparse import urljoin
import os
from textwrap import dedent
from tambo import Transport
import chacractl

logger = logging.getLogger(__name__)

class Binary(object):
    _help = dedent("""
    operate binaries on a remote chacra instance.
    """)
    help_menu = "upload, update metadata, or delete binaries"
    options = ['post']

    def __init__(self, argv):
        self.argv = argv

    @property
    def base_url(self):
        return os.path.join(
            chacractl.config['url'], 'binaries'
        )

    def sanitize_stdin(self, line):
        """
        lines may come with newlines and leading slashes make sure
        they are clean so that they can be processed
        """
        line = line.strip('\n').strip('/').strip('./')
        return line.split('/')[-1]

    def sanitize_url(self, url_part):
        # get rid of the leading slash to prevent issues when joining
        url = url_part.lstrip('/')

        # and add a trailing slash so that the POST is done at the correct
        # canonical url
        if not url.endswith('/'):
            url = "%s/" % url
        return url

    def main(self):
        self.parser = Transport(self.argv, options=self.options)
        self.parser.catch_help = self._help
        self.parser.parse_args()
        logger.info(self.base_url)
        # handle posting binaries:
        if self.parser.has('post'):
            url_part = self.parser.get('post').strip('/')
            if not sys.stdin.isatty():
                # read from stdin
                logger.info('reading input from stdin')
                for line in sys.stdin.readlines():
                    filename = self.sanitize_stdin(line)
                    if not filename:
                        continue
                    url = os.path.join(self.base_url, url_part)
                    logger.warning('post %s %s', url, filename)
            else:
                url = os.path.join(self.base_url, url_part)
                logger.warning('post %s', url)
