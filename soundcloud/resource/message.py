import datetime
from dataclasses import dataclass

from soundcloud.resource.base import BaseData
from soundcloud.resource.user import BasicUser

@dataclass
class Message(BaseData):
    content: str
    conversation_id: str
    sender: BasicUser
    sender_urn: str
    sender_type: str
    sent_at: datetime.datetime