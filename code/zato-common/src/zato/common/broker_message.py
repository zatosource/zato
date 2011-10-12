# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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

# Bunch
from bunch import Bunch

MESSAGE_TYPE = Bunch()
MESSAGE_TYPE.TO_SINGLETON = b'0000'
MESSAGE_TYPE.TO_PARALLEL = b'0001'

SCHEDULER = Bunch()
SCHEDULER.CREATE = b'1000'
SCHEDULER.EDIT = b'1001'
SCHEDULER.DELETE = b'1002'
SCHEDULER.EXECUTE = b'1003'

ZERO_MQ_SOCKET = Bunch()
ZERO_MQ_SOCKET.CLOSE = b'1100'

#SECURITY.BASIC_AUTH_ = 110