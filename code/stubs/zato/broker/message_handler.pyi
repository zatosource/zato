from typing import Any

from logging import getLogger
from traceback import format_exc
from bunch import bunchify
from zato.common.broker_message import code_to_name
from zato.common.typing_ import any_, anydict, dataclass, strnone

class BrokerMessageResult:
    was_handled: bool
    response: any_
    action_code: strnone
    action_name: str

def handle_broker_msg(msg: anydict, context: any_) -> BrokerMessageResult: ...
