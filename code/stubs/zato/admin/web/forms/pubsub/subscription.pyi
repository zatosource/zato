from typing import Any

import logging
from django import forms
from zato.admin.web.util import get_pubsub_security_choices
from zato.common.api import PubSub

def get_rest_endpoint_choices(req: Any) -> None: ...

class CreateForm(forms.Form):
    is_delivery_active: Any
    is_pub_active: Any
    topic_id: Any
    sec_base_id: Any
    delivery_type: Any
    push_type: Any
    rest_push_endpoint_id: Any
    push_service_name: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ..., req: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_delivery_active: Any
    is_pub_active: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ..., req: Any = ...) -> None: ...
