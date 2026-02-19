from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from pytz import common_timezones
from zato.admin.web import DATE_FORMATS, TIME_FORMATS

class BasicSettingsForm(forms.Form):
    timezone: Any
    date_format: Any
    time_format: Any
    totp_key: Any
    totp_key_label: Any
    totp_key_provision_uri: Any
    def __init__(self: Any, initial: Any, *args: Any, **kwargs: Any) -> None: ...
