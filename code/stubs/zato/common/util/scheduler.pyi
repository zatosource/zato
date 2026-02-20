from typing import Any, TYPE_CHECKING

from contextlib import closing
from copy import deepcopy
from datetime import datetime
from json import dumps
from logging import getLogger
from time import sleep
from traceback import format_exc
from bunch import Bunch
from zato.common.api import SCHEDULER
from zato.common.odb.model import Cluster, IntervalBasedJob, Job, Service
import cloghandler
from zato.common.typing_ import any_, list_
from zato.scheduler.api import SchedulerAPI


def wait_for_odb_service_by_odb(session: any_, cluster_id: int, service_name: str) -> None: ...

def wait_for_odb_service_by_api(api: SchedulerAPI, service_name: str) -> None: ...

def _add_scheduler_job(api: SchedulerAPI, job_data: Bunch, spawn: bool, source: str) -> None: ...

def add_startup_jobs_to_odb_by_odb(cluster_id: int, odb: any_, jobs: any_) -> None: ...

def load_scheduler_jobs_by_odb(api: SchedulerAPI, odb: any_, cluster_id: int, spawn: bool = ...) -> None: ...

def add_startup_jobs_to_odb_by_api(api: SchedulerAPI, jobs: list_[Bunch]) -> None: ...

def load_scheduler_jobs_by_api(api: SchedulerAPI, spawn: bool) -> None: ...
