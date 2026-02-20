from typing import Any, TYPE_CHECKING

from zato.common.typing_ import strlist


class GroupObject:
    _config_attrs: Any
    id: Any
    is_active: Any
    type: Any
    name: Any
    name_slug: Any
    members: Any
    def __init__(self: Any) -> None: ...
