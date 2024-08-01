import os

import pytest

from soundcloud import SoundCloud


@pytest.fixture(scope="session")
def client(request):
    return SoundCloud(auth_token=os.environ.get("auth_token"))
