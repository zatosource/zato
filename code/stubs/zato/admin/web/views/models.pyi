from typing import Any, TYPE_CHECKING

from dataclasses import dataclass, field


class ContentRow:
    label: str
    widget: str
    value_key: str
    element_id: str
    default_text: str
    is_copyable: bool
    copy_id: str
    spinner: bool
    options: list
    input_width: str
