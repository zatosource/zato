# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ZatoCommand, ZATO_INFO_FILE

# bzrlib
from bzrlib.lazy_import import lazy_import

lazy_import(globals(), """

    # stdlib
    import json, os
""")

class ComponentVersion(ZatoCommand):
    file_needed = ZATO_INFO_FILE

    def execute(self, args):
        info = json.load(open(os.path.join(args.path, self.file_needed))) # noqa
        self.logger.info(info['version'])
