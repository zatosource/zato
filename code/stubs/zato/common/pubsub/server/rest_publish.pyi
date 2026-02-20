from typing import Any, TYPE_CHECKING

import os
from datetime import datetime
from logging import getLogger
from werkzeug.wrappers import Request
from zato.common.api import PubSub
from zato.common.pubsub.models import PubMessage, APIResponse, _base_response
from zato.common.pubsub.server.rest_base import BadRequestException, BaseRESTServer, UnauthorizedException
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.api import as_bool
from zato.common.typing_ import any_, anydict

_min_priority = PubSub.Message.Priority_Min
_max_priority = PubSub.Message.Priority_Max
_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration

class PubSubRESTServerPublish(BaseRESTServer):
    server_type: Any
    def on_publish(self: Any, cid: str, environ: anydict, start_response: any_, topic_name: str) -> _base_response: ...
