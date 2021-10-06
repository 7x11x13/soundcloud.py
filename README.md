# soundcloud.py

Python wrapper for some of the v2 SoundCloud API

## Installation

```bash
pip install soundcloud-v2
```

## Example

```python
from soundcloud import SoundCloud

sc = SoundCloud("client_id", "auth_token")
me = sc.get_user_by_username("7x11x13")
assert me.permalink == "7x11x13"
```

## License
[MIT](https://choosealicense.com/licenses/mit/)