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

# stdlib
import logging
from hashlib import sha256
from httplib import FORBIDDEN, NOT_FOUND, responses

# Zato
from zato.common import HTTPException, ZATO_NONE

logger = logging.getLogger(__name__)

class Security(object):
    """ Performs all the HTTP/SOAP-related security checks.
    """
    def handle(self, rid, url_data, request_data, body, headers):
        """ Calls other concrete security methods as appropriate.
        """
        
        # No security at all for that URL.
        if url_data.sec_def == ZATO_NONE:
            return True
        
        sec_def, sec_def_type = url_data.sec_def, url_data.sec_def.type
        
        handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
        getattr(self, handler_name)(rid, sec_def, request_data, body, headers)
    
    def _handle_security_tech_acc(self, rid, sec_def, request_data, body, headers):
        """ Handles the 'tech_acc' security config type.
        """
        zato_headers = ('X_ZATO_USER', 'X_ZATO_PASSWORD')
        
        for header in zato_headers:
            if not headers.get(header, None):
                msg = ("[{0}] The header [{1}] doesn't exist or is empty, URI=[{2}, "
                      "headers=[{3}]]").\
                        format(rid, header, request_data.uri, headers)
                logger.error(msg)
                raise HTTPException(FORBIDDEN)

        msg_template = '[{0}] The {1} is incorrect, URI:[{2}], X_ZATO_USER:[{3}]'

        if headers['X_ZATO_USER'] != sec_def.name:
            logger.error(msg_template.format(rid, 'username', request_data.uri, headers['X_ZATO_USER']))
            raise HTTPException(FORBIDDEN)
        
        incoming_password = sha256(headers['X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()
        
        if incoming_password != sec_def.password:
            logger.error(msg_template.format(rid, 'password', request_data.uri, headers['X_ZATO_USER']))
            raise HTTPException(FORBIDDEN)

class RequestHandler(object):
    """ Handles all the incoming HTTP/SOAP requests.
    """
    def __init__(self, security=None, soap_handler=None):
        self.security = security
        self.soap_handler = soap_handler
    
    def handle(self, rid, url_data, transport, task, thread_ctx):
        if url_data:
            
            body = task.request_data.getBodyStream().getvalue()
            headers = task.request_data.headers            
            
            self.security.handle(rid, url_data, task.request_data, body, headers)
            
            # TODO: Shadow out any passwords that may be contained in HTTP
            # headers or in the message itself. Of course, that only applies
            # to auth schemes we're aware of (HTTP Basic Auth, WSS etc.)
            
            # Fetch the response.
            return self.soap_handler.handle(rid, body, headers, thread_ctx)

        else:
            msg = "The URL [{0}] doesn't exist".format(task.request_data.uri)
            logger.warn(msg, rid)
            raise HTTPException(NOT_FOUND)
