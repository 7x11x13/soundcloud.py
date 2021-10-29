# soundcloud.py

[![Tests](https://github.com/7x11x13/soundcloud.py/actions/workflows/ci.yml/badge.svg)](https://github.com/7x11x13/soundcloud.py/actions/workflows/ci.yml)[![Coverage Status](https://coveralls.io/repos/github/7x11x13/soundcloud.py/badge.svg?branch=main)](https://coveralls.io/github/7x11x13/soundcloud.py?branch=main)

Python wrapper for some of the v2 SoundCloud API

## Installation

```bash
pip install soundcloud-v2
```

## Example

```python
from soundcloud import SoundCloud

sc = SoundCloud("client_id", "auth_token")
assert sc.is_client_id_valid()
assert sc.is_auth_token_valid()
me = sc.get_user_by_username("7x11x13")
assert me.permalink == "7x11x13"
```

## License
[MIT](https://choosealicense.com/licenses/mit/)