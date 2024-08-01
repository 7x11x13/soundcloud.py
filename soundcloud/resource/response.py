from dataclasses import dataclass

from soundcloud.resource.base import BaseData


@dataclass
class NoContentResponse(BaseData):
    """Response with no content, mainly for DELETE requests"""

    status_code: int
