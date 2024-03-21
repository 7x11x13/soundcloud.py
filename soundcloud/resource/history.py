from dataclasses import dataclass
from typing import List

# from dacite import from_dict

from soundcloud.resource.base import BaseData
from soundcloud.resource.track import BasicTrack


"""Hello copilot!

Write a dataclass that has the following attributes:

1. An int attribute called played_at
2. An int attribute called track_id
3. A basic track attribute called track

The dataclass should be called TaggedTrack

"""

# This was inaccurate so here's my version
@dataclass
class TaggedTrack(BaseData):
    played_at: int
    track_id: int
    track: BasicTrack

"""Hello copilot!

Write a dataclass that has the following attributes:

1. A list of tagged tracks called tracks

The dataclass should be called History

"""

@dataclass
class History(BaseData):
    tracks: List[TaggedTrack]


"""Hello copilot!
Based on my the entire soundcloud.py directory write a dataclass that represents Listening history of a user and stores the all tracks along with their nested data.
"""

# @dataclass
# class History(BaseData):
#     tracks: list[AlbumPlaylistNoTracks]
