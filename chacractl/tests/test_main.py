import os
from textwrap import dedent
import pytest
import chacractl
from chacractl.main import ChacraCtl


class TestApiCredentials(object):

    def chacractl_templates():
        template_base = dedent("""
        url = "https://example"
        user = "chacra user"
        key = "secret"
        """)
        return [
            (template_base, True),
            (template_base + 'ssl_verify = True', True),
            (template_base + 'ssl_verify = False', False),
            (template_base + 'ssl_verify = "path/to/ca"', 'path/to/ca')
        ]

    @pytest.mark.parametrize('template,expected', chacractl_templates())
    def test_ssl_verify(self, tmpdir, monkeypatch, template, expected):
        config_path = tmpdir.join('.chacractl')
        config_path.write(template)
        monkeypatch.setattr(os.path, 'expanduser', lambda _: str(config_path))
        c = ChacraCtl()
        c.api_credentials()
        assert chacractl.config['ssl_verify'] == expected
