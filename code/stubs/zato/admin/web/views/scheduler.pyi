from typing import Any

import logging
from datetime import datetime
from io import StringIO
from traceback import format_exc
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from pytz import UTC
from zato.admin.web import from_user_to_utc, from_utc_to_user
from zato.admin.web.views import get_js_dt_format, method_allowed, Delete as _Delete, parse_response_data
from zato.admin.settings import job_type_friendly_names
from zato.admin.web.forms.scheduler import IntervalBasedSchedulerJobForm, OneTimeSchedulerJobForm
from zato.common.api import SCHEDULER, TRACE1
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
from zato.common.odb.model import IntervalBasedJob, Job
from zato.common.util.api import pprint
from zato.common.py23_.past.builtins import unicode
from zato.common.util.api import parse_datetime
from dateutil.parser import parse as parse_datetime

def _get_start_date(start_date: Any) -> None: ...

def _one_time_job_def(user_profile: Any, start_date: Any) -> None: ...

def _interval_based_job_def(user_profile: Any, start_date: Any, repeats: Any, weeks: Any, days: Any, hours: Any, minutes: Any, seconds: Any) -> None: ...

def _get_success_message(action: Any, job_type: Any, job_name: Any) -> None: ...

def _get_create_edit_message(user_profile: Any, cluster: Any, params: Any, form_prefix: Any = ...) -> None: ...

def _get_create_edit_one_time_message(user_profile: Any, cluster: Any, params: Any, form_prefix: Any = ...) -> None: ...

def _get_create_edit_interval_based_message(user_profile: Any, cluster: Any, params: Any, form_prefix: Any = ...) -> None: ...

def _create_one_time(client: Any, user_profile: Any, cluster: Any, params: Any) -> None: ...

def _create_interval_based(client: Any, user_profile: Any, cluster: Any, params: Any) -> None: ...

def _edit_one_time(client: Any, user_profile: Any, cluster: Any, params: Any) -> None: ...

def _edit_interval_based(client: Any, user_profile: Any, cluster: Any, params: Any) -> None: ...

def index(req: Any) -> None: ...

class Delete(_Delete):
    url_name: Any
    error_message: Any
    service_name: Any

def execute(req: Any, job_id: Any, cluster_id: Any) -> None: ...

def get_definition(req: Any, start_date: Any, repeats: Any, weeks: Any, days: Any, hours: Any, minutes: Any, seconds: Any) -> HttpResponse: ...
