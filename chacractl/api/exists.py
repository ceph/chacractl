import os
from textwrap import dedent
import logging
import requests
from tambo import Transport
import chacractl
from chacractl.util import retry
from chacractl.decorators import catches, requests_errors


logger = logging.getLogger(__name__)


class Exists(object):
    _help = dedent("""
    Check if a given URL part exists already. Mainly does a HEAD request to the
    given endpoint. If the URL does not exist it will return a non-zero exit
    status (404).

    For example:

        chacractl exists binaries/ceph-deploy/master/debian/wheezy

    Positional Arguments:

    [URL]        The endpoint, starting with the full url part (sans fqdn)
    """)
    help_menu = "check if a given URL part exists already"
    options = []

    def __init__(self, argv):
        self.argv = argv
        self.base_url = chacractl.config['url']

    def sanitize_url(self, url_part):
        # get rid of the leading slash to prevent issues when joining
        url = url_part.lstrip('/')

        # and add a trailing slash so that the request is done at the correct
        # canonical url
        if not url.endswith('/'):
            url = "%s/" % url
        return url

    @catches(requests.exceptions.HTTPError, handler=requests_errors)
    @retry()
    def head(self, url):
        logger.info('HEAD: %s', url)
        exists = requests.head(
            url,
            auth=chacractl.config['credentials'],
            verify=chacractl.config['ssl_verify'])
        exists.raise_for_status()

    def main(self):
        self.parser = Transport(self.argv, options=self.options)
        self.parser.catch_help = self._help
        self.parser.parse_args()
        if self.parser.unknown_commands:
            url_part = self.sanitize_url(self.parser.unknown_commands[-1])
            url = os.path.join(self.base_url, url_part)
            return self.head(url)
        else:
            logger.error('no url was passed in')
