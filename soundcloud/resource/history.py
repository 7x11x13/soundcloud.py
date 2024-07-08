from dataclasses import dataclass

from soundcloud.resource.base import BaseData
from soundcloud.resource.track import BasicTrack


@dataclass
class HistoryItem(BaseData):
    """Item in user's listen history"""

    played_at: int
    track: BasicTrack
    track_id: int
