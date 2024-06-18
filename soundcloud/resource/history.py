from dataclasses import dataclass
from soundcloud.resource.base import BaseData
from soundcloud.resource.track import BasicTrack


@dataclass
class HistoryItem(BaseData):
    played_at: int
    track: BasicTrack
    track_id: int