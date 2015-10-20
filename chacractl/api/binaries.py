import logging
import sys
import os
from textwrap import dedent

import requests
from tambo import Transport

import chacractl

logger = logging.getLogger(__name__)


class Binary(object):
    _help = dedent("""
    Operate binaries on a remote chacra instance.

    Creating a new binary::

        chacractl binary create project/ref/distro/distro_version/arch /path/to/binary

    Options:

    create        Creates a new binary at a given distro version architecture
    """)
    help_menu = "create, update metadata, or delete binaries"
    options = ['create']

    def __init__(self, argv):
        self.argv = argv

    @property
    def base_url(self):
        return os.path.join(
            chacractl.config['url'], 'binaries'
        )

    def sanitize_filename(self, line):
        """
        lines may come with newlines and leading slashes make sure
        they are clean so that they can be processed
        """
        line = line.strip('\n')
        if os.path.isfile(line):
            return os.path.abspath(line)

    def sanitize_url(self, url_part):
        # get rid of the leading slash to prevent issues when joining
        url = url_part.lstrip('/')

        # and add a trailing slash so that the POST is done at the correct
        # canonical url
        if not url.endswith('/'):
            url = "%s/" % url
        return url

    def post(self, url, filepath):
        filename = os.path.basename(filepath)
        file_url = os.path.join(url, filename) + '/'
        exists = requests.head(file_url)
        if exists.status_code == 200:
            logger.warning('resource already exists, will not upload')
            logger.warning('SKIP %s', file_url)
            return
        logger.info('POSTing file: %s', filepath)
        with open(filepath) as binary:
            response = requests.post(
                url,
                files={'file': binary},
                auth=chacractl.config['credentials'])
        if response.status_code > 201:
            logger.warning("%s -> %s", response.status_code, response.text)

    def main(self):
        self.parser = Transport(self.argv, options=self.options)
        self.parser.catch_help = self._help
        self.parser.parse_args()

        # handle posting binaries:
        if self.parser.has('create'):
            url_part = self.sanitize_url(self.parser.get('create'))
            if not sys.stdin.isatty():
                # read from stdin
                logger.info('reading input from stdin')
                for line in sys.stdin.readlines():
                    filename = self.sanitize_filename(line)
                    if not filename:
                        continue
                    url = os.path.join(self.base_url, url_part)
                    self.post(url, filename)
            else:
                filepath = self.sanitize_filename(self.argv[-1])
                if not filepath:
                    logger.warning(
                        'provided path does not exist: %s', self.argv[-1]
                    )
                    return
                url = os.path.join(self.base_url, url_part)
                self.post(url, filepath)
