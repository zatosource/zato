from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.cli import ZatoCommand, common_odb_opts
from zato.common.odb import drop_all

class Delete(ZatoCommand):
    needs_password_confirm: Any
    opts: Any
    def execute(self: Any, args: Any) -> None: ...
