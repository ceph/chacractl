import logging
import sys
import os
from textwrap import dedent

import requests
from tambo import Transport

import chacractl
from chacractl.util import retry

logger = logging.getLogger(__name__)


class Project(object):
    _help = dedent("""
    Handle projects on a remote chacra instance.

    Creating a new project::

        chacractl project create project

    Options:

    create        Creates a new project
    """)
    help_menu = "create projects"
    options = ['create']

    def __init__(self, argv):
        self.argv = argv

    @property
    def base_url(self):
        return os.path.join(
            chacractl.config['url'], 'binaries'
        )

    def sanitize_url(self, url_part):
        # get rid of the leading slash to prevent issues when joining
        url = url_part.lstrip('/')

        # and add a trailing slash so that the request is done at the correct
        # canonical url
        if not url.endswith('/'):
            url = "%s/" % url
        return url

    @retry()
    def post(self, url):
        exists = requests.head(url, verify=chacractl.config['ssl_verify'])

        if exists.status_code == 200:
            logger.warning('resource exists, will not upload')
            logger.warning('SKIP %s', url)
            return
        elif exists.status_code == 404:
            logger.info('POSTing to project: %s', url)
            response = requests.post(
                url,
                auth=chacractl.config['credentials'],
                verify=chacractl.config['ssl_verify'])
        if response.status_code > 201:
            logger.warning("%s -> %s", response.status_code, response.text)
            response.raise_for_status()

    @retry()
    def delete(self, url):
        # XXX This exists here but it is not yet implemented, e.g. nothing
        # calls this method
        exists = requests.head(url, verify=chacractl.config['ssl_verify'])
        if exists.status_code == 404:
            logger.warning('project already deleted')
            logger.warning('SKIP %s', url)
            return
        logger.info('DELETE project: %s', url)
        response = requests.delete(
            url,
            auth=chacractl.config['credentials'],
            verify=chacractl.config['ssl_verify'])
        if response.status_code > 201:
            logger.warning("%s -> %s", response.status_code, response.text)

    def main(self):
        self.parser = Transport(self.argv, options=self.options)
        self.parser.catch_help = self._help
        self.parser.parse_args()

        # handle posting projects:
        if self.parser.has('create'):
            url_part = self.sanitize_url(self.parser.get('create'))
            if not sys.stdin.isatty():
                # read from stdin
                logger.info('reading input from stdin')
                for line in sys.stdin.readlines():
                    url = os.path.join(self.base_url, url_part)
                    self.post(url)
            else:
                url = os.path.join(self.base_url, url_part)
                self.post(url)
        # XXX this exists here but it not yet enabled from the CLI
        elif self.parser.has('delete'):
            url_part = self.sanitize_url(self.parser.get('delete'))
            url = os.path.join(self.base_url, url_part)
            self.delete(url)
