from typing import Any, TYPE_CHECKING

from operator import itemgetter
from django import forms
from zato.common.ext.future.utils import iteritems
from zato.admin.settings import delivery_friendly_name
from zato.common.api import AMQP


class CreateForm(forms.Form):
    name: Any
    is_active: Any
    address: Any
    username: Any
    password: Any
    delivery_mode: Any
    priority: Any
    content_type: Any
    content_encoding: Any
    expiration: Any
    pool_size: Any
    user_id: Any
    app_id: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
