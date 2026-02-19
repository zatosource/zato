from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from copy import deepcopy
from uuid import uuid4
from zato.common.api import ADAPTER_PARAMS, HTTPException
from zato.common.json_internal import dumps, loads
from zato.server.service import Service

class JSONAdapter(Service):
    outconn: Any
    method: Any
    params_to_qs: Any
    load_response: Any
    params: Any
    force_in_qs: Any
    apply_params: Any
    raise_error_on: Any
    def get_call_params(self: Any) -> None: ...
    def handle(self: Any) -> None: ...
