from typing import Any

from zato.cli import ZatoCommand
from zato.common.util.api import asbool
from zato.common.typing_ import dictlist, stranydict
import os
import sys
from zato.cli.enmasse.client import get_session_from_server_dir
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.util.api import get_client_from_server_conf
from zato.common.ext.configobj_ import ConfigObj

class Enmasse(ZatoCommand):
    opts: dictlist
    def get_cluster_id(self: Any, args: Any) -> None: ...
    def execute(self: Any, args: Any) -> None: ...
    @staticmethod
    def format_object_name(item: Any) -> None: ...
