# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os

# Zato
from zato.cli import ZatoCommand
from zato.common import ZATO_INFO_FILE

class ComponentVersion(ZatoCommand):
    file_needed = ZATO_INFO_FILE

    def execute(self, args):
        info = json.load(open(os.path.join(args.path, self.file_needed))) # noqa
        self.logger.info(info['version'])
