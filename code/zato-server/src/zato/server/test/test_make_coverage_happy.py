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

# Importing all Zato modules here makes sure nosetests --coverage will report
# the code coverage for, well, all Zato modules. It follows that any new Zato
# module must be imported here.
#
# http://groups.google.com/group/nose-users/browse_thread/thread/1a48c8a121972986
#

from zato. import context, main, sample, scheduler, server, soap, sqlpool

# And now make pyflakes (http://divmod.org/trac/wiki/DivmodPyflakes) happy
# otherwise it will warn about code being imported but not used.
context, main, sample, scheduler, server, soap, sqlpool
