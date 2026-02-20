from typing import Any, TYPE_CHECKING

from zato.cli import common_odb_opts, ZatoCommand
from zato.common.odb.model import Base


class Create(ZatoCommand):
    opts: Any
    def allow_empty_secrets(self: Any) -> None: ...
    def execute(self: Any, args: Any, show_output: Any = ...) -> None: ...
