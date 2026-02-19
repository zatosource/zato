from typing import Any

from django import forms
from zato.admin.web.forms import add_services, DataFormatForm
from zato.common.api import AMQP

class CreateForm(DataFormatForm):
    name: Any
    is_active: Any
    address: Any
    username: Any
    password: Any
    queue: Any
    consumer_tag_prefix: Any
    pool_size: Any
    ack_mode: Any
    prefetch_count: Any
    service: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ..., req: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
