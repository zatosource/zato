from typing import Any

import os
from zato.common.util.config import get_config_object, update_config_file
from zato.server.service import AsIs, Bool, Int, SIOElem
from zato.server.service.internal import AdminService, ChangePasswordBase
from bunch import Bunch
from zato.common.ext.configobj_ import ConfigObj
from zato.common.typing_ import any_, anylist, strdict

class ModuleCtx:
    StaticID: Any

def set_kvdb_config(server_config: strdict, input_data: Bunch, redis_sentinels: str) -> None: ...

class GetList(AdminService):
    def get_data(self: Any) -> anylist: ...
    def handle(self: Any) -> None: ...

class Edit(AdminService):
    def handle(self: Any) -> None: ...

class ChangePassword(ChangePasswordBase):
    password_required: Any
    def handle(self: Any) -> None: ...
