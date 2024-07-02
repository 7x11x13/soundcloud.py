import os

import pytest

from soundcloud import SoundCloud


@pytest.fixture(scope="session")
def client(request):
    return SoundCloud(os.environ["client_id"], os.environ["auth_token"])
