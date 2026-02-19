from typing import Any

from __future__ import absolute_import, division
from zato.common.ext.dictalchemy import utils

class DictableModel(object):
    asdict: Any
    fromdict: Any
    __iter__: Any
