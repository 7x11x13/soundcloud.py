# ruff: noqa
"""
# soundcloud.py

[![Tests](https://github.com/7x11x13/soundcloud.py/actions/workflows/ci.yml/badge.svg)](https://github.com/7x11x13/soundcloud.py/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/7x11x13/soundcloud.py/badge.svg?branch=main)](https://coveralls.io/github/7x11x13/soundcloud.py?branch=main)
[![Supported Python Versions](https://img.shields.io/badge/python-3.7%2C%203.8%2C%203.9%2C%203.10%2C%203.11%2C%203.12-blue.svg)](https://pypi.org/project/soundcloud-v2/)
[![Version](https://img.shields.io/pypi/v/soundcloud-v2.svg)](https://pypi.org/project/soundcloud-v2/)
[![License](https://img.shields.io/pypi/l/soundcloud-v2.svg)](https://pypi.org/project/soundcloud-v2/)
[![Monthly Downloads](https://pepy.tech/badge/soundcloud-v2/month)](https://pepy.tech/project/soundcloud-v2)

Python wrapper for some of the internal v2 SoundCloud API (read/GET only methods). Does not require an API key.

### Note: This is NOT the official [SoundCloud developer API](https://developers.soundcloud.com/docs/api/guide)

SoundCloud is not accepting any more application registration requests [^1] so
I made this library so developers can use SoundCloud's internal API for their projects.


[^1]: https://docs.google.com/forms/d/e/1FAIpQLSfNxc82RJuzC0DnISat7n4H-G7IsPQIdaMpe202iiHZEoso9w/closedform

## Installation

```bash
pip install soundcloud-v2
```

## Documentation

https://7x11x13.xyz/soundcloud.py

## Example

```python
from soundcloud import SoundCloud

sc = SoundCloud(auth_token="auth_token")
assert sc.is_client_id_valid()
assert sc.is_auth_token_valid()
me = sc.get_user_by_username("7x11x13")
assert me.permalink == "7x11x13"
```

## Notes on `auth_token`
Some methods require authentication in the form of an OAuth2 access token.
You can find your token in your browser cookies for SoundCloud under the name "oauth_token".
A new token will be generated each time you log out and log back in.

## Notes on `**kwargs`
All API methods have a `**kwargs` argument which you can use to pass extra, undocumented
arguments to the SoundCloud v2 API in case I missed some parameter which you find useful.
If this is the case, feel free to create an issue or pull request to document the missing
argument.

## License
[MIT](https://choosealicense.com/licenses/mit/)

"""

from soundcloud.exceptions import *
from soundcloud.exceptions import __all__ as ex_all
from soundcloud.resource import *
from soundcloud.resource import __all__ as res_all
from soundcloud.soundcloud import *
from soundcloud.soundcloud import __all__ as sc_all

__version__ = "1.6.0"

__all__ = sc_all + ex_all + res_all
