import os

from soundcloud import SoundCloud


def test_full_auth_token():
    sc = SoundCloud("invalid", "OAuth " + os.environ["auth_token"])
    assert (not sc.is_client_id_valid()) and sc.is_auth_token_valid()

def test_valid_client_id_and_auth_token(client: SoundCloud):
    assert client.is_client_id_valid() and client.is_auth_token_valid()

def test_invalid_client_id_valid_auth_token():
    sc = SoundCloud("invalid", os.environ["auth_token"])
    assert (not sc.is_client_id_valid()) and sc.is_auth_token_valid()
    
def test_invalid_auth_token_and_client_id():
    sc = SoundCloud("invalid", "invalid")
    assert (not sc.is_auth_token_valid()) and (not sc.is_client_id_valid())
    
def test_invalid_auth_token_valid_client_id():
    sc = SoundCloud(os.environ["client_id"], "invalid")
    assert (not sc.is_auth_token_valid()) and sc.is_client_id_valid()
    
def test_me(client: SoundCloud):
    me = client.get_me()
    assert me.username == "7x11x13"
    
def test_dynamic_client_id():
    sc = SoundCloud()
    assert sc.is_client_id_valid()
