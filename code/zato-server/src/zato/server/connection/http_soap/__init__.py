# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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

# stdlib
from httplib import BAD_REQUEST, FORBIDDEN, NOT_FOUND, UNAUTHORIZED

# Zato
from zato.common import HTTPException

class ClientHTTPError(HTTPException):
    def __init__(self, cid, msg, status):
        super(ClientHTTPError, self).__init__(cid, msg, status)
        
class BadRequest(ClientHTTPError):
    def __init__(self, cid, msg):
        super(BadRequest, self).__init__(cid, msg, BAD_REQUEST)
        
class Forbidden(ClientHTTPError):
    def __init__(self, cid, msg):
        super(Forbidden, self).__init__(cid, msg, FORBIDDEN)
        
class NotFound(ClientHTTPError):
    def __init__(self, cid, msg):
        super(NotFound, self).__init__(cid, msg, NOT_FOUND)
        
class Unauthorized(ClientHTTPError):
    def __init__(self, cid, msg, challenge):
        super(Unauthorized, self).__init__(cid, msg, UNAUTHORIZED)
        self.challenge = challenge
