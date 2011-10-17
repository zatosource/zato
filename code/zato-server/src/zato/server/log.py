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

# stdlib
from logging import Logger

# Zato
from zato.common.log_message import NULL_CNO, NULL_RID

class ZatoLogger(Logger):
    """ A custom subclass which turns parameters not understood otherwise
    into an 'extra' dictionary of the base class.
    """
    def info(self, msg, rid=NULL_RID, cno=NULL_CNO, *args, **kwargs):
        return Logger.info(self, msg, extra={'rid':rid, 'cno':cno})
        
    def warn(self, msg, rid, cno, *args, **kwargs):
        return super(ZatoLogger, self).warn(msg, extra={'rid':rid, 'cno':cno})
    
    #def debug
    #info
    #warning
    #warn = warning
    #log