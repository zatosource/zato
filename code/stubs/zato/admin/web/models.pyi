from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django.db import models
from django.contrib.auth.models import User
from zato.admin.web import DATE_FORMATS, MONTH_YEAR_FORMATS, TIME_FORMATS
from zato.common.json_internal import loads

def _on_delete(*unused_args: Any, **unused_kwargs: Any) -> None: ...

class TOTPData:
    def __init__(self: Any) -> None: ...

class UserProfile(models.Model):
    user: Any
    timezone: Any
    date_format: Any
    time_format: Any
    opaque1: Any
    __unicode__: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def __repr__(self: Any) -> None: ...
    def get_totp_data(self: Any) -> None: ...

class ClusterColorMarker(models.Model):
    user_profile: Any
    cluster_id: Any
    color: Any
    __unicode__: Any
    def __repr__(self: Any) -> None: ...
