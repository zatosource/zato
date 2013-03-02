# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at gefira.pl>

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
import os
from contextlib import closing

# anyjson
import anyjson

# Bunch
from bunch import Bunch

# Zato
from zato.cli import ZatoCommand, ZATO_INFO_FILE
from zato.client import AnyServiceInvoker, CID_NO_CLIP, DEFAULT_MAX_CID_REPR, DEFAULT_MAX_RESPONSE_REPR
from zato.common.crypto import CryptoManager
from zato.common.odb.model import Cluster, HTTPBasicAuth, HTTPSOAP, Server, Service
from zato.common.util import get_config
        
class Invoke(ZatoCommand):
    """ Invokes a service by its name
    """
    file_needed = ZATO_INFO_FILE
    
    opts = [
        {'name':'path', 'help':'Path in the file-system to a server the service is deployed on'},
        {'name':'name', 'help':'Name of the service to invoke'},
        {'name':'--payload', 'help':'Payload to invoke the service with'},
        {'name':'--headers', 'help':'Additional HTTP headers the service invoker will receive in format of header-name=header-value; header2-name=header2-value'},
        {'name':'--channel', 'help':'Channel the service will be invoked through', 'default':'invoke'},
        {'name':'--data-format', 'help':"Payload's data format", 'default': 'json'},
        {'name':'--transport', 'help':'Transport to invoke the service over'},
        {'name':'--url-path', 'help':'URL path zato.service.invoke is exposed on', 'default':'/zato/admin/invoke'},
        {'name':'--max-cid-repr', 'help':'How many characters of a CID to print out in verbose mode, defaults to {}, use {} to print the whole of it'.format(
            DEFAULT_MAX_CID_REPR, CID_NO_CLIP), 'default':DEFAULT_MAX_CID_REPR},
        {'name':'--max-response-repr', 'help':'How many characters of a response to print out in verbose mode, defaults to {}'.format(
            DEFAULT_MAX_RESPONSE_REPR), 'default':DEFAULT_MAX_RESPONSE_REPR},
    ]
    
    def execute(self, args):
        repo_dir = os.path.join(os.path.abspath(os.path.join(self.original_dir, args.path)), 'config', 'repo')
        config = get_config(repo_dir, 'server.conf')
        priv_key_location = os.path.abspath(os.path.join(repo_dir, config.crypto.priv_key_location))
        
        cm = CryptoManager(priv_key_location=priv_key_location)
        cm.load_keys()
        
        engine_args = Bunch()
        engine_args.odb_type = config.odb.engine
        engine_args.odb_user = config.odb.username
        engine_args.odb_password = cm.decrypt(config.odb.password)
        engine_args.odb_host = config.odb.host
        engine_args.odb_db_name = config.odb.db_name
        
        engine = self._get_engine(engine_args)
        session = self._get_session(engine)
        
        auth = None
        headers = {}
        
        with closing(session) as session:
            cluster = session.query(Server).\
                filter(Server.token == config.main.token).\
                one().cluster
            
            channel = session.query(HTTPSOAP).\
                filter(HTTPSOAP.cluster_id == cluster.id).\
                filter(HTTPSOAP.url_path == args.url_path).\
                one()
            
            if channel.security_id:
                security = session.query(HTTPBasicAuth).\
                    filter(HTTPBasicAuth.id == channel.security_id).\
                    first()
                
                if security:
                    auth = (security.username, security.password)
                    
        if args.headers:
            for pair in args.headers.strip().split(';'):
                k, v = pair.strip().split('=', 1)
                headers[k] = v
                    
        client = AnyServiceInvoker('http://{}'.format(config.main.gunicorn_bind), auth, args.url_path,
            max_response_repr=int(args.max_response_repr), max_cid_repr=int(args.max_cid_repr))
        response = client.invoke(args.name, args.payload, headers, args.channel, args.data_format, args.transport)
        
        if response.ok:
            self.logger.info(response.data or '(None)')
        else:
            self.logger.error(response.details)
            
        if args.verbose:
            self.logger.debug('inner.text:[{}]'.format(response.inner.text))
            self.logger.debug('response:[{}]'.format(response))

