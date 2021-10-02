from dataclasses import dataclass

from soundcloud.resource.base import BaseData

@dataclass
class WebProfile(BaseData):
    url: str
    network: str
    title: str
    
@dataclass
class WebProfileUsername(WebProfile):
    username: str