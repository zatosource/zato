# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        info = json.load(open(os.path.join(args.path, self.file_needed)))
        self.logger.info(info['version'])
