from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.admin.web.forms import add_select
from zato.common.api import LDAP

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    get_info: Any
    ip_mode: Any
    connect_timeout: Any
    auto_bind: Any
    server_list: Any
    pool_name: Any
    pool_size: Any
    pool_exhaust_timeout: Any
    pool_keep_alive: Any
    pool_max_cycles: Any
    pool_lifetime: Any
    pool_ha_strategy: Any
    username: Any
    auth_type: Any
    sasl_mechanism: Any
    is_read_only: Any
    should_check_names: Any
    use_auto_range: Any
    should_return_empty_attrs: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...

class EditForm(CreateForm):
    is_active: Any
    use_sasl_external: Any
    use_auto_range: Any
    should_return_empty_attrs: Any
