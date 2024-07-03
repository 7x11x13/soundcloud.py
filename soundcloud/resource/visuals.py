from dataclasses import dataclass
from typing import Tuple

from soundcloud.resource.base import BaseData


@dataclass(frozen=True)
class Visual(BaseData):
    urn: str
    entry_time: int
    visual_url: str


@dataclass(frozen=True)
class Visuals(BaseData):
    urn: str
    enabled: bool
    visuals: Tuple[Visual, ...]
