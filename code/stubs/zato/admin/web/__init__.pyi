from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from dateutil.relativedelta import relativedelta
from django.template.defaultfilters import date as django_date_filter
from zato.common.util.api import from_local_to_utc as _from_local_to_utc, from_utc_to_local as _from_utc_to_local

class _Format:
    def __init__(self: Any, frontend: Any, python: Any) -> None: ...

def last_hour_start_stop(now: Any) -> None: ...

def from_utc_to_user(dt: Any, user_profile: Any, format: Any = ...) -> None: ...

def from_user_to_utc(dt: Any, user_profile: Any, format: Any = ...) -> None: ...
