from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division
from zato.common.ext.dictalchemy import utils


class DictableModel(object):
    asdict: Any
    fromdict: Any
    __iter__: Any
