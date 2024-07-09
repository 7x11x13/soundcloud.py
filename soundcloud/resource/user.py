import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

from soundcloud.resource.base import BaseData
from soundcloud.resource.visuals import Visuals


@dataclass
class Product(BaseData):
    id: str


@dataclass
class CreatorSubscription(BaseData):
    product: Product


@dataclass
class Badges(BaseData):
    """User badges"""

    pro: bool
    pro_unlimited: bool
    verified: bool


@dataclass
class BasicUser(BaseData):
    """User with partial information"""

    avatar_url: str
    first_name: str
    followers_count: int
    full_name: str
    id: int
    kind: str
    last_modified: datetime.datetime
    last_name: str
    permalink: str
    permalink_url: str
    uri: str
    urn: str
    username: str
    verified: bool
    city: Optional[str]
    country_code: Optional[str]
    badges: Badges
    station_urn: Optional[str]
    station_permalink: Optional[str]


@dataclass
class User(BasicUser):
    """User with full information"""

    comments_count: int
    created_at: datetime.datetime
    creator_subscriptions: Tuple[CreatorSubscription, ...]
    creator_subscription: CreatorSubscription
    description: Optional[str]
    followings_count: int
    groups_count: int
    likes_count: Optional[int]
    playlist_likes_count: Optional[int]
    playlist_count: int
    reposts_count: Optional[int]
    track_count: int
    visuals: Optional[Visuals]


@dataclass
class MissingUser(BaseData):
    """Deleted user"""

    id: int
    kind: str


@dataclass
class UserStatus(BaseData):
    status: str
    timestamp: str


@dataclass
class UserEmail(BaseData):
    """Email address associated with a user"""

    address: str
    confirmed: bool
    id: int
    kind: str
    last_modified: datetime.datetime
    primary: bool
    urn: str
    user_id: str
