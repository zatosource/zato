from typing import Any

import os
import logging
from django.core.wsgi import get_wsgi_application
from zato.admin.zato_settings import update_globals
from zato.common.json_internal import loads
from zato.common.util.open_ import open_r
