from typing import Any

from zato.common.typing_ import dataclass
from zato.server.service import Model

class ExpiryHookInput(Model):
    current_app: str
    username: str
    default_expiry: int
