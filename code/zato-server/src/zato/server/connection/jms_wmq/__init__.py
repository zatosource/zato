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

# Zato
from zato.common.broker_message import DEFINITION, JMS_WMQ_CONNECTOR
from zato.server.connection import BaseConnection, BaseConnector

class BaseJMSWMQConnector(BaseConnector):
    
    def filter(self, msg):
        """ Can we handle the incoming message?
        """
        if super(BaseJMSWMQConnector, self).filter(msg):
            return True
        
        elif msg.action == JMS_WMQ_CONNECTOR.CLOSE:
            return self.odb.odb_data['token'] == msg['odb_token']
        
        elif msg.action in(DEFINITION.JMS_WMQ_EDIT, DEFINITION.JMS_WMQ_DELETE):
            return self.def_.id == msg.id
