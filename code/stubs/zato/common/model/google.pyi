from typing import Any, TYPE_CHECKING

from zato.common.typing_ import dataclass
from zato.server.service import Model


class GoogleAPIDescription(Model):
    id: str
    name: str
    title: str
    version: str
    title_full: str
