import os

import pytest

from soundcloud import SoundCloud


@pytest.fixture(scope="session")
def client(request):
    if not os.environ.get("client_id"):
        print(
            "You didn't set the client_id environment variable. One will be generated for you."
        )
        os.environ["client_id"] = SoundCloud.generate_client_id()

    return SoundCloud(os.environ.get("client_id"), os.environ.get("auth_token"))
