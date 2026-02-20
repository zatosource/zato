from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division


class DictalchemyError(Exception):
    ...

class UnsupportedRelationError(DictalchemyError):
    relation_key: Any
    def __init__(self: Any, relation_key: Any) -> None: ...
    def __str__(self: Any) -> None: ...

class MissingRelationError(DictalchemyError):
    relation_key: Any
    def __init__(self: Any, relation_key: Any) -> None: ...
    def __str__(self: Any) -> None: ...
