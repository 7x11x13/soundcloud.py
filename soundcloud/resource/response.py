from dataclasses import dataclass

@dataclass
class NoContentResponse:
    """Response with no content, mainly for DELETE requests"""

    status_code: int