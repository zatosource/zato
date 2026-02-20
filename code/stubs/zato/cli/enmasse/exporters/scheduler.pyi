from typing import Any

import logging
from zato.common.odb.model import to_json
from zato.common.odb.query import job_list
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.odb.model import Job
from zato.common.typing_ import anydict, list_

class SchedulerExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> job_def_list: ...
