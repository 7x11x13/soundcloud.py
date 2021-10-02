import datetime
from dataclasses import dataclass

from soundcloud.resource.base import BaseData
from soundcloud.resource.message import Message
from soundcloud.resource.user import BasicUser

@dataclass
class Conversation(BaseData):
    id: str
    last_message: Message
    read: bool
    started_at: datetime.datetime
    summary: str
    users: list[BasicUser]