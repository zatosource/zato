from typing import Any

from dataclasses import dataclass
from zato.server.service import Model
from zato.common.typing_ import list_, list_field
from zato.common.util.file_system import fs_safe_now
from zato.common.typing_ import any_

class Config:
    ParamName: str
    MacroName: str
    DataLayout: str
    SchemaVersion: str
    KeyStyle: str
    ValueStyle: str
    UserLinkPattern: str
    RowPattern: str
    MacroTemplate: str

class Row(Model):
    key: str
    value: str

class PageProperties:
    param_name: str
    key_style: str
    value_style: str
    macro_name: str
    row_pattern: str
    macro_template: str
    schema_version: str
    user_link_pattern: str
    rows: list_[Row]
    param_name: Any
    local_id: Any
    rows: Any
    def __init__(self: Any, param_name: str = ..., local_id: str = ...) -> None: ...
    def get_user_link(self: Any, account_id: str) -> str: ...
    def append(self: Any, key: any_, value: any_) -> Row: ...
    def get_result(self: Any) -> None: ...
