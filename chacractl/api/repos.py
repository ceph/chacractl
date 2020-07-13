import os
from textwrap import dedent
import logging
import requests
from tambo import Transport
import chacractl
from chacractl.util import retry
from chacractl.decorators import catches, requests_errors


logger = logging.getLogger(__name__)


class Repo(object):
    _help = dedent("""
    Operate on repositories on a remote chacra instance. Both `recreate` and
    `update` calls are not immediate. They rely on the async service managing
    repos which usually have a delay applied to them.

    Options:

    recreate        Mark a repository to be removed and created from scratch
                    again.
    update          Repository will get updated by running the repo tools on
                    it again.
    """)
    help_menu = "recreate, delete, or update repositories"
    options = ['recreate', 'delete', 'update']

    def __init__(self, argv):
        self.argv = argv

    @property
    def base_url(self):
        return os.path.join(
            chacractl.config['url'], 'repos'
        )

    @catches(requests.exceptions.HTTPError, handler=requests_errors)
    @retry()
    def post(self, url):
        exists = requests.head(
            url,
            auth=chacractl.config['credentials'],
            verify=chacractl.config['ssl_verify'])
        exists.raise_for_status()
        logger.info('POST: %s', url)
        response = requests.post(
            url,
            auth=chacractl.config['credentials'],
            verify=chacractl.config['ssl_verify'])
        response.raise_for_status()
        json = response.json()
        for k, v in json.items():
            logger.info("%s: %s", k, v)

    @catches(requests.exceptions.HTTPError, handler=requests_errors)
    @retry()
    def delete(self, url):
        exists = requests.head(url, verify=chacractl.config['ssl_verify'])
        if exists.status_code == 404:
            logger.warning('repo already deleted')
            logger.warning('SKIP %s', url)
            return
        logger.info('DELETE repo: %s', url)
        response = requests.delete(
            url,
            auth=chacractl.config['credentials'],
            verify=chacractl.config['ssl_verify'])
        if response.status_code < 200 or response.status_code > 299:
            logger.warning("%s -> %s", response.status_code, response.text)

    def main(self):
        self.parser = Transport(self.argv, options=self.options)
        self.parser.catch_help = self._help
        self.parser.parse_args()
        recreate = self.parser.get('recreate')
        update = self.parser.get('update')
        delete = self.parser.get('delete')
        if recreate:
            url_part = os.path.join(recreate, 'recreate')
            url = os.path.join(self.base_url, url_part)
            self.post(url)
        elif update:
            url_part = os.path.join(update, 'update')
            url = os.path.join(self.base_url, url_part)
            self.post(url)
        elif delete:
            url_part = os.path.join(delete, 'delete')
            url = os.path.join(self.base_url, url_part)
            self.delete(url)
