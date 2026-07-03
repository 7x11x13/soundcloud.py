class ClientIDGenerationError(Exception):
    """
    Raised when a client ID could not be dynamically generated.
    """


class NoValidClientIDError(Exception):
    """
    Raised when none of the available client IDs appear valid.
    """


__all__ = ["ClientIDGenerationError", "NoValidClientIDError"]
