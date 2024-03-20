import datetime
from dataclasses import dataclass
from typing import List, Optional

from soundcloud.resource.base import BaseData
from soundcloud.resource.base_item import BaseItem
from soundcloud.resource.user import User, BasicUser
from soundcloud.resource.visuals import Visuals

@dataclass
class Format(BaseData):
    protocol: str
    mime_type: str
    
@dataclass
class Transcoding(BaseData):
    url: str
    preset: str
    duration: int
    snipped: bool
    format: Format
    quality: str
    
@dataclass
class Media(BaseData):
    transcodings: List[Transcoding]
    
@dataclass
class PublisherMetadata(BaseData):
    id: str
    urn: str
    contains_music: bool

@dataclass
class BaseTrack(BaseItem):
    caption: Optional[str]
    commentable: bool
    comment_count: Optional[int]
    downloadable: bool
    download_count: Optional[int]
    full_duration: int
    has_downloads_left: bool
    playback_count: Optional[int]
    purchase_title: Optional[str]
    purchase_url: Optional[str]
    state: str
    streamable: bool
    urn: str
    visuals: Optional[Visuals]
    waveform_url: str
    media: Media
    station_urn: str
    station_permalink: str
    track_authorization: str
    monetization_model: str
    policy: str

@dataclass
class Track(BaseTrack):
    user: User

@dataclass
class BasicTrack(BaseTrack):
    user: BasicUser
    
@dataclass
class MiniTrack(BaseData):
    id: int
    kind: str
    monetization_model: str
    policy: str
    
@dataclass
class CommentTrack(BaseData):
    artwork_url: Optional[str]
    caption: Optional[str]
    id: int
    kind: str
    last_modified: datetime.datetime
    permalink: str
    permalink_url: str
    public: bool
    secret_token: Optional[str]
    sharing: str
    title: str
    uri: str
    urn: str
    user_id: int
    full_duration: int
    duration: int
    display_date: datetime.datetime
    media: Media
    station_urn: str
    station_permalink: str
    track_authorization: str
    monetization_model: str
    policy: str
    user: BasicUser