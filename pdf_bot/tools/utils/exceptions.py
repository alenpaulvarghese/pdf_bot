# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-


class BaseExceptiion(Exception):
    """Base class for all exceptions"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ServerShuttingDown(Exception):
    """Raise if servers are about to be shutdown"""

    def __init__(self) -> None:
        super().__init__("Server is shutting down please try again later")
