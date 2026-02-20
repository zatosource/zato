from typing import Any, TYPE_CHECKING

from dataclasses import dataclass
from zato.server.service import Model


class Member(Model):
    id: int
    name: str
    type: str
    group_id: int
    security_id: int
    sec_type: str
    username: str
    password: str
    header_value: str
