from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.common.odb.model import Cluster

class ODBPostProcess:
    def __init__(self: Any, session: Any, cluster: Any, cluster_id: Any) -> None: ...
    def run(self: Any) -> None: ...
