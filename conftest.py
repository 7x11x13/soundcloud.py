import os

import pytest

from soundcloud import SoundCloud


@pytest.fixture(scope="session")
def client(request):
    os.environ["auth_token"] = "2-296070-526801914-fEHP3bawXM2Bew"
    if not os.environ.get("client_id"):
        print("You didn't set the client_id environment variable. One will be generated for you.")
        os.environ["client_id"] = SoundCloud.generate_client_id(SoundCloud)

    return SoundCloud(os.environ.get("client_id"), os.environ.get("auth_token"))
