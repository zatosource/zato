from typing import Any

from zato.common.ext.imbox.messages import Messages
from zato.common.ext.imbox.vendors.helpers import merge_two_dicts

class GmailMessages(Messages):
    authentication_error_message: Any
    hostname: Any
    name: Any
    FOLDER_LOOKUP: Any
    GMAIL_IMAP_ATTRIBUTE_LOOKUP_DIFF: Any
    def __init__(self: Any, connection: Any, parser_policy: Any, **kwargs: Any) -> None: ...
