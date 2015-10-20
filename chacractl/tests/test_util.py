import os
from chacractl import util


class TestDefaultConfig(object):

    def test_create_config(self, tmpdir):
        path = str(tmpdir)
        config_path = os.path.join(path, '.chacractl')
        util.default_config_path = lambda: config_path
        util.ensure_default_config()
        assert os.path.exists(config_path)

    def test_config_has_some_defaults(self, tmpdir):
        path = str(tmpdir)
        config_path = os.path.join(path, '.chacractl')
        util.default_config_path = lambda: config_path
        util.ensure_default_config()
        msg = "This file was automatically generated"
        with open(config_path, 'r') as f:
            assert msg in f.read()

    def test_config_will_not_overwrite(self, tmpdir):
        path = str(tmpdir)
        config_path = os.path.join(path, '.chacractl')
        with open(config_path, 'w') as f:
            f.write('')
        util.default_config_path = lambda: config_path
        util.ensure_default_config()
        with open(config_path, 'r') as f:
            assert f.read() == ''


class TestLoadConfig(object):

    def test_no_config(self, tmpdir):
        path = str(tmpdir)
        config_path = os.path.join(path, '.chacractl')
        util.default_config_path = lambda: config_path
        module = util.load_config()
        assert module is None

    def test_config_is_loaded(self, tmpdir):
        path = str(tmpdir)
        config_path = os.path.join(path, '.chacractl')
        util.default_config_path = lambda: config_path
        util.ensure_default_config()
        module = util.load_config()
        assert module.user == 'chacra user'
        assert module.key == 'secret'
