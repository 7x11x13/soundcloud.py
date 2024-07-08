from dataclasses import dataclass

from soundcloud.resource.base import BaseData


@dataclass
class OriginalDownload(BaseData):
    """Contains a download link for a track"""

    redirectUri: str
