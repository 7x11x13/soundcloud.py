from dataclasses import dataclass
from typing import Optional

from soundcloud.resource.base import BaseData


@dataclass
class WebProfile(BaseData):
    url: str
    network: str
    title: str
    username: Optional[str]
