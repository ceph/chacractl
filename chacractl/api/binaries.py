import logging
import sys
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from textwrap import dedent
from hashlib import sha512

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from tambo import Transport

import chacractl
from chacractl.util import retry

logger = logging.getLogger(__name__)


class Binary(object):
    _help = dedent("""
    Operate binaries on a remote chacra instance.

    Creating a new binary::

        chacractl binary create project/ref/distro/distro_version/arch /path/to/binary

    Options:

    create        Creates a new binary at a given distro version architecture
    delete        Deletes an existing binary from chacra
    --force       If the resource exists, force the upload
    """)
    help_menu = "create, update metadata, or delete binaries"
    options = ['create', '--force', 'delete']

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

        # and add a trailing slash so that the request is done at the correct
        # canonical url
        if not url.endswith('/'):
            url = "%s/" % url
        return url

    def get_checksum(self, filepath):
        chsum = sha512()
        with open(filepath, 'rb') as binary:
            for chunk in iter(lambda: binary.read(4096), b''):
                chsum.update(chunk)
        return chsum.hexdigest()

    @retry()
    def upload_is_verified(self, arch_url, filename, digest):
        r = requests.get(arch_url, verify=chacractl.config['ssl_verify'])
        r.raise_for_status()
        arch_data = r.json()
        remote_digest = arch_data[filename]['checksum']
        verified = remote_digest == digest
        if not verified:
            logging.error(
                    'Checksum mismatch: server has wrong checksum for %s',
                    filename)
            logging.error('local checksum: %s', digest)
            logging.error('remote checksum: %s', remote_digest)
        return verified

    @retry()
    def post(self, url, filepath):
        filename = os.path.basename(filepath)
        file_url = os.path.join(url, filename) + '/'
        exists = requests.head(file_url, verify=chacractl.config['ssl_verify'])
        digest = self.get_checksum(filepath)

        if exists.status_code == 200:
            if not self.force:
                logger.warning(
                    'resource exists and --force was not used, will not upload'
                )
                logger.warning('SKIP %s', file_url)
                return
            return self.put(file_url, filepath)
        elif exists.status_code == 404:
            length = os.path.getsize(filepath)
            logger.info('POSTing file: %s', filepath)
            mpart = MultipartEncoder(
                fields={'file': (filename, open(filepath, 'rb'), 'text/plain')}
            )

            response = requests.post(
                url,
                data=mpart,
                headers={
                    'Content-Type': mpart.content_type,
                    'Content-Length': '%d' % length,
                },
                auth=chacractl.config['credentials'],
                verify=chacractl.config['ssl_verify'])
            if response.status_code > 201:
                logger.warning("%s -> %s", response.status_code, response.text)
                response.raise_for_status()
        if not self.upload_is_verified(url, filename, digest):
            # Since this is a new file, attempt to delete it
            logging.error('Deleting corrupted file from server...')
            self.delete(file_url)
            raise SystemExit(
                    'Checksum mismatch: remote server has wrong checksum for %s'
                    % filepath)
    @retry()
    def put(self, url, filepath):
        filename = os.path.basename(filepath)
        logger.info('resource exists and --force was used, will re-upload')
        logger.info('PUTing file: %s', filepath)
        digest = self.get_checksum(filepath)
        length = os.path.getsize(filepath)
        mpart = MultipartEncoder(
            fields={'file': (filename, open(filepath, 'rb'), 'text/plain')}
        )
        response = requests.put(
            url,
            data=mpart,
            headers={
                'Content-Type': mpart.content_type,
                'Content-Length': '%d' % length,
            },
            auth=chacractl.config['credentials'],
            verify=chacractl.config['ssl_verify'])
        if response.status_code > 201:
            logger.warning("%s -> %s", response.status_code, response.text)
        # trim off binary filename
        url = url.rsplit('/', 2)[0] + "/"
        if not self.upload_is_verified(url, filename, digest):
            # Maybe the old file with a different digest is still there, so
            # don't delete it
            raise SystemExit(
                    'Checksum mismatch: server has wrong checksum for %s!'
                    % filepath)
    @retry()
    def delete(self, url):
        exists = requests.head(url, verify=chacractl.config['ssl_verify'])
        if exists.status_code == 404:
            logger.warning('resource already deleted')
            logger.warning('SKIP %s', url)
            return
        logger.info('DELETE file: %s', url)
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
        self.force = self.parser.has('--force')

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

        elif self.parser.has('delete'):
            if self.parser.get('delete') is None:
                raise SystemExit('Specify a URL to delete a binary.')
            url_part = self.sanitize_url(self.parser.get('delete'))
            url = os.path.join(self.base_url, url_part)
            self.delete(url)
