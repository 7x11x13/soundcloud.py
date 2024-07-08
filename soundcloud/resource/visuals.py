from dataclasses import dataclass
from typing import Tuple

from soundcloud.resource.base import BaseData


@dataclass
class Visual(BaseData):
    urn: str
    entry_time: int
    visual_url: str


@dataclass
class Visuals(BaseData):
    urn: str
    enabled: bool
    visuals: Tuple[Visual, ...]
