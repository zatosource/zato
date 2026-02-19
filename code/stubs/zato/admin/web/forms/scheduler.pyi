from typing import Any

from django import forms
from zato.admin.web.forms import add_services

class _Base(forms.Form):
    id: Any
    name: Any
    is_active: Any
    service: Any
    extra: Any
    start_date: Any
    def __init__(self: Any, prefix: Any, req: Any) -> None: ...

class OneTimeSchedulerJobForm(_Base):
    ...

class IntervalBasedSchedulerJobForm(_Base):
    weeks: Any
    days: Any
    hours: Any
    minutes: Any
    seconds: Any
    start_date: Any
    repeats: Any
