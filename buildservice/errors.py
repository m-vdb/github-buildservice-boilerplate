"""Common exceptions"""

class CannotCreateHook(Exception):
    """Raised when Webhook cannot be created"""


class MalformattedToken(Exception):
    """Raised when a received token is malformatted"""


class MissingToken(Exception):
    """Raised when we cannot find a token."""


class InvalidStatus(Exception):
    """Raises when the Build status is invalid."""
