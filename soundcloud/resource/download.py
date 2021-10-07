from dataclasses import dataclass

from soundcloud.resource.base import BaseData

@dataclass
class OriginalDownload(BaseData):
    redirectUri: str