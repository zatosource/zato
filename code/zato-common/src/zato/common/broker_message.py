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

MESSAGE = Bunch()
MESSAGE.MESSAGE_TYPE_LENGTH = 4
MESSAGE.TOKEN_LENGTH = 32
MESSAGE.TOKEN_START = MESSAGE.MESSAGE_TYPE_LENGTH
MESSAGE.TOKEN_END = MESSAGE.MESSAGE_TYPE_LENGTH + MESSAGE.TOKEN_LENGTH
MESSAGE.PAYLOAD_START = MESSAGE.MESSAGE_TYPE_LENGTH + MESSAGE.TOKEN_LENGTH
MESSAGE.NULL_TOKEN = '0' * 32

MESSAGE_TYPE = Bunch()
MESSAGE_TYPE.TO_SINGLETON = b'0000'
MESSAGE_TYPE.TO_PARALLEL_PULL = b'0001'
MESSAGE_TYPE.TO_PARALLEL_SUB = b'0002'
MESSAGE_TYPE.USER_DEFINED_START = b'1000'

SCHEDULER = Bunch()
SCHEDULER.CREATE = b'10000'
SCHEDULER.EDIT = b'10001'
SCHEDULER.DELETE = b'10002'
SCHEDULER.EXECUTE = b'10003'
SCHEDULER.JOB_EXECUTED = b'10003'

ZMQ_SOCKET = Bunch()
ZMQ_SOCKET.CLOSE = b'10100'

SECURITY = Bunch()
SECURITY.BASIC_AUTH_CREATE = b'10200'
SECURITY.BASIC_AUTH_EDIT = b'10201'
SECURITY.BASIC_AUTH_DELETE = b'10202'
SECURITY.BASIC_AUTH_CHANGE_PASSWORD = b'10203'

SECURITY = Bunch()
SECURITY.TECH_ACC_CREATE = b'10300'
SECURITY.TECH_ACC_EDIT = b'10301'
SECURITY.TECH_ACC_DELETE = b'10302'
SECURITY.TECH_ACC_CHANGE_PASSWORD = b'10303'


code_to_name = {}

# To prevent 'RuntimeError: dictionary changed size during iteration'
bunch_name, bunch = None, None

for bunch_name, bunch in globals().items():
    if isinstance(bunch, Bunch) and not bunch is Bunch:
        if bunch not in(MESSAGE, MESSAGE_TYPE):
            for code_name, code_value in bunch.items():
                code_name = bunch_name + '_' + code_name
                code_to_name[code_value] = code_name
                
del bunch_name, bunch, code_name, code_value