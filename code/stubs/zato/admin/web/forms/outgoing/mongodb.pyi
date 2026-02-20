from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.admin.web.forms import add_select
from zato.common.api import MONGODB

default = MONGODB.DEFAULT
timeout = default.TIMEOUT

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    username: Any
    app_name: Any
    replica_set: Any
    auth_source: Any
    auth_mechanism: Any
    pool_size_max: Any
    connect_timeout: Any
    socket_timeout: Any
    server_select_timeout: Any
    wait_queue_timeout: Any
    max_idle_time: Any
    hb_frequency: Any
    is_tz_aware: Any
    document_class: Any
    compressor_list: Any
    zlib_level: Any
    write_to_replica: Any
    write_timeout: Any
    is_write_journal_enabled: Any
    is_write_fsync_enabled: Any
    should_retry_write: Any
    read_pref_type: Any
    read_pref_tag_list: Any
    read_pref_max_stale: Any
    server_list: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...

class EditForm(CreateForm):
    is_active: Any
    tls_match_hostname: Any
    should_retry_write: Any
