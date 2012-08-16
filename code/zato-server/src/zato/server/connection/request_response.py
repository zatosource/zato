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

# Zato
from zato.common.broker_message import MESSAGE_TYPE, SERVICE

def should_store(service_id):
    """ Decides whether a service's request/response pair should be kept in the DB.
    TODO: Make sure only actual service requests and responses are getting added
    and not, say, WSDLs.
    """
    return True

def store(broker_client, cid, service_id, req_timestamp, resp_timestamp, request, response):
    """ Stores a service's request/response pair.
    """
    params = {}
    params['action'] = SERVICE.SET_REQUEST_RESPONSE
    params['cid'] = cid
    params['service_id'] = service_id
    params['req_timestamp'] = req_timestamp.isoformat()
    params['resp_timestamp'] = resp_timestamp.isoformat()
    params['request'] = request
    params['response'] = response
    
    broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_ANY)
