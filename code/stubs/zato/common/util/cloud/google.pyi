from typing import Any, TYPE_CHECKING

from zato.common.model.google import GoogleAPIDescription
from zato.common.typing_ import list_
import os
from operator import itemgetter
from googleapiclient.discovery_cache import DISCOVERY_DOC_DIR as root_dir
from zato.common.typing_ import cast_
from zato.common.util.open_ import open_r
from zato.common.util.json_ import JSONParser


def get_api_list() -> list_[GoogleAPIDescription]: ...
