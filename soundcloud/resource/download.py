from dataclasses import dataclass

from soundcloud.resource.base import BaseData


@dataclass(frozen=True)
class OriginalDownload(BaseData):
    """Contains a download link for a track"""

    redirectUri: str
