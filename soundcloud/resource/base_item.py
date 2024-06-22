import datetime
from dataclasses import dataclass
from typing import List, Optional

from soundcloud.resource.base import BaseData


@dataclass
class BaseItem(BaseData):
    artwork_url: Optional[str]
    created_at: datetime.datetime
    description: Optional[str]
    duration: int
    embeddable_by: str
    genre: Optional[str]
    id: int
    kind: str
    label_name: Optional[str]
    last_modified: datetime.datetime
    licence: Optional[str]
    likes_count: Optional[int]
    permalink: str
    permalink_url: str
    public: bool
    purchase_title: Optional[str]
    purchase_url: Optional[str]
    release_date: Optional[str]
    reposts_count: Optional[int]
    secret_token: Optional[str]
    sharing: str
    tag_list: str
    title: str
    uri: str
    user_id: int
    display_date: str

    def get_all_tags(self) -> List[str]:
        tags = []
        if self.genre:
            tags.append(self.genre)
        return tags + [tag.strip() for tag in self.tag_list.split('"') if tag.strip()]
