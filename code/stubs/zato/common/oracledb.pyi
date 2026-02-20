from typing import Any

import oracledb as oracledb_impl

class OracleParam:
    is_out: Any
    value: Any
    size: Any
    var: Any
    def __init__(self: Any, value: Any = ..., size: Any = ...) -> None: ...
    def bind(self: Any, cursor: Any) -> None: ...
    def get(self: Any) -> None: ...

class NumberIn(OracleParam):
    def bind(self: Any, cursor: Any) -> None: ...

class StringIn(OracleParam):
    def bind(self: Any, cursor: Any) -> None: ...

class FixedCharIn(OracleParam):
    def bind(self: Any, cursor: Any) -> None: ...

class DateTimeIn(OracleParam):
    def bind(self: Any, cursor: Any) -> None: ...

class BlobIn(OracleParam):
    def bind(self: Any, cursor: Any) -> None: ...

class ClobIn(OracleParam):
    def bind(self: Any, cursor: Any) -> None: ...

class _OutBase(OracleParam):
    is_out: Any

class NumberOut(_OutBase):
    def bind(self: Any, cursor: Any) -> None: ...

class StringOut(_OutBase):
    def bind(self: Any, cursor: Any) -> None: ...

class FixedCharOut(_OutBase):
    def bind(self: Any, cursor: Any) -> None: ...

class DateTimeOut(_OutBase):
    def bind(self: Any, cursor: Any) -> None: ...

class BlobOut(_OutBase):
    def bind(self: Any, cursor: Any) -> None: ...

class ClobOut(_OutBase):
    def bind(self: Any, cursor: Any) -> None: ...

class RowsOut(_OutBase):
    def bind(self: Any, cursor: Any) -> None: ...
