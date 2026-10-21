"""Errors raised by the service layer.

Services know nothing about HTTP. The routers translate these into
HTTP status codes (404, 409, ...).
"""


class NotFoundError(Exception):
    """The requested record does not exist."""


class DuplicateError(Exception):
    """The record would break a uniqueness rule (e.g. same ISBN)."""

    

class BusinessRuleError(Exception):
    """The action is not allowed by a library rule."""