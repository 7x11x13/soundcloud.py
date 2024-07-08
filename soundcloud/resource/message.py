import datetime
from dataclasses import dataclass
from typing import Union

from soundcloud.resource.base import BaseData
from soundcloud.resource.user import BasicUser, MissingUser


@dataclass
class Message(BaseData):
    """Single DM between two users"""

    content: str
    conversation_id: str
    sender: Union[BasicUser, MissingUser]
    sender_urn: str
    sender_type: str
    sent_at: datetime.datetime
