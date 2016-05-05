import sys
import pytest


@pytest.fixture(autouse=True)
def clear_config(request):
    sys.modules.pop('chacractl', None)
