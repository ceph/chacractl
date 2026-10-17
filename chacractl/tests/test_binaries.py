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

    def __init__(self, monkeypatch, checksums, posts=(), listing_status=200):
        self.checksums = list(checksums)
        self.posts = list(posts)
        self.listing_status = listing_status
        self.posted_fields = []
        self.puts = 0
        self.deletes = 0
        monkeypatch.setattr(binaries.requests, 'post', self.post)
        monkeypatch.setattr(binaries.requests, 'get', self.get)
        monkeypatch.setattr(binaries.Binary, 'put', self.put)
        monkeypatch.setattr(binaries.Binary, 'delete', self.delete)

    def post(self, url, data, **kw):
        self.posted_fields.append(set(data.fields))
        return FakeResponse(self.posts.pop(0))

    def get(self, *args, **kw):
        if self.listing_status != 200:
            return FakeResponse(self.listing_status)
        checksum = self.checksums[0]
        if len(self.checksums) > 1:
            self.checksums.pop(0)
        if checksum is None:
            return FakeResponse(404)
        return FakeResponse(200, {FILENAME: {'checksum': checksum}})

    def put(self, *args):
        self.puts += 1

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

    @pytest.mark.parametrize('conflict', [400, 409])
    def test_retry_after_timeout_finds_upload(self, path, server, conflict):
        # the proxy gives up with a 504, the retried POST gets a 400, or
        # a 409 from newer chacra, because the first upload has landed in
        # the meantime
        s = server([None, None, DIGEST], posts=[504, conflict])
        upload(path)
        assert s.posts == []

    def test_existing_upload_with_other_checksum_fails(self, path, server):
        server([None, 'other'], posts=[400])
        with pytest.raises(requests.HTTPError):
            upload(path)

    def test_force_is_sent_with_post(self, path, server):
        s = server([None, DIGEST], posts=[200])
        upload(path, force=True)
        assert s.posted_fields == [{'file', 'force'}]

    @pytest.mark.parametrize('force,checksum,puts', [
        (True, DIGEST, 0),
        (False, 'other', 0),
        (True, 'other', 1),
    ])
    def test_existing_upload(self, path, server, force, checksum, puts):
        s = server([checksum])
        upload(path, force)
        assert s.posted_fields == []
        assert s.puts == puts

    def test_listing_error_fails(self, path, server):
        s = server([DIGEST], listing_status=502)
        with pytest.raises(requests.HTTPError):
            upload(path)
        assert s.posted_fields == []

    def test_missing_upload_is_not_deleted(self, path, server):
        s = server([None], posts=[201])
        with pytest.raises(SystemExit, match='not found on the server'):
            upload(path)
        assert s.deletes == 0
