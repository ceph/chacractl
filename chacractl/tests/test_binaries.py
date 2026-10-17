from hashlib import sha512

import pytest
import requests

import chacractl
from chacractl import util
from chacractl.api import binaries


URL = 'https://chacra.example/binaries/ceph/ref/sha1/centos/9/x86_64/'
FILENAME = 'ceph-test-debuginfo.rpm'
DIGEST = sha512(b'payload').hexdigest()


class FakeResponse(object):

    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self.text = ''
        self._json = json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                '%d error' % self.status_code, response=self)


class FakeServer(object):
    """
    `checksums` is what the listing reports for FILENAME on each GET, the
    last one sticks. None means the file is not listed, and chacra
    answers 404 for a listing with no binaries.
    """

    def __init__(self, monkeypatch, checksums, puts=(), listing_status=200):
        self.checksums = list(checksums)
        self.puts = list(puts)
        self.listing_status = listing_status
        self.put_headers = []
        self.deletes = 0
        monkeypatch.setattr(binaries.requests, 'put', self.put)
        monkeypatch.setattr(binaries.requests, 'get', self.get)
        monkeypatch.setattr(binaries.Binary, 'delete', self.delete)

    def put(self, url, data, headers, **kw):
        assert url == URL + FILENAME + '/'
        self.put_headers.append(headers)
        return FakeResponse(self.puts.pop(0))

    def get(self, *args, **kw):
        if self.listing_status != 200:
            return FakeResponse(self.listing_status)
        checksum = self.checksums[0]
        if len(self.checksums) > 1:
            self.checksums.pop(0)
        if checksum is None:
            return FakeResponse(404)
        return FakeResponse(200, {FILENAME: {'checksum': checksum}})

    def delete(self, *args):
        self.deletes += 1


@pytest.fixture
def path(tmpdir, monkeypatch):
    monkeypatch.setitem(chacractl.config, 'credentials', ('user', 'key'))
    monkeypatch.setitem(chacractl.config, 'ssl_verify', True)
    monkeypatch.setattr(util.time, 'sleep', lambda _: None)
    path = tmpdir.join(FILENAME)
    path.write('payload')
    return str(path)


@pytest.fixture
def server(monkeypatch):
    return lambda *args, **kw: FakeServer(monkeypatch, *args, **kw)


def upload(path, force=False):
    b = binaries.Binary([])
    b.force = force
    b.post(URL, path)


class TestPost(object):

    def test_creates_with_precondition(self, path, server):
        s = server([None, DIGEST], puts=[201])
        upload(path)
        assert s.put_headers[0]['If-None-Match'] == '*'

    def test_force_replaces_without_precondition(self, path, server):
        s = server(['other', DIGEST], puts=[200])
        upload(path, force=True)
        assert 'If-None-Match' not in s.put_headers[0]

    def test_retry_after_timeout_finds_upload(self, path, server):
        # the proxy gives up with a 504, the retried PUT fails its
        # precondition because the first upload has landed meanwhile
        s = server([None, None, DIGEST], puts=[504, 412])
        upload(path)
        assert s.puts == []

    def test_precondition_failed_with_other_checksum_skips(self, path,
                                                           server):
        s = server([None, 'other'], puts=[412])
        upload(path)
        assert s.puts == []

    @pytest.mark.parametrize('force,checksum', [
        (True, DIGEST),
        (False, 'other'),
    ])
    def test_existing_upload_is_skipped(self, path, server, force,
                                        checksum):
        s = server([checksum])
        upload(path, force)
        assert s.put_headers == []

    def test_listing_error_fails(self, path, server):
        s = server([DIGEST], listing_status=502)
        with pytest.raises(requests.HTTPError):
            upload(path)
        assert s.put_headers == []

    def test_missing_upload_is_not_deleted(self, path, server):
        s = server([None], puts=[201])
        with pytest.raises(SystemExit, match='not found on the server'):
            upload(path)
        assert s.deletes == 0

    @pytest.mark.parametrize('force,status,deletes', [
        (False, 201, 1),
        (True, 200, 0),
    ])
    def test_corrupted_upload(self, path, server, force, status, deletes):
        s = server([None, 'corrupted'], puts=[status])
        with pytest.raises(SystemExit, match='Checksum mismatch'):
            upload(path, force)
        assert s.deletes == deletes
