from typing import Any, TYPE_CHECKING

from zato.cli import ZatoCommand
from zato.client import CID_NO_CLIP, DEFAULT_MAX_CID_REPR, DEFAULT_MAX_RESPONSE_REPR
from zato.common.api import BROKER, ZATO_INFO_FILE
from zato.common.const import ServiceConst
from zato.common.api import DATA_FORMAT
from zato.common.util.api import get_client_from_server_conf


class Invoke(ZatoCommand):
    file_needed: Any
    opts: Any
    def execute(self: Any, args: Any) -> None: ...
