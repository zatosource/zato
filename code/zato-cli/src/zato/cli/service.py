# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from contextlib import closing

# Bunch
from bunch import Bunch

# Zato
from zato.cli import ZatoCommand, ZATO_INFO_FILE
from zato.client import AnyServiceInvoker, CID_NO_CLIP, DEFAULT_MAX_CID_REPR, DEFAULT_MAX_RESPONSE_REPR
from zato.common import BROKER, DATA_FORMAT
from zato.common.crypto import CryptoManager
from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP, Server
from zato.common.util import get_config
        
class Invoke(ZatoCommand):
    """ Invokes a service by its name
    """
    file_needed = ZATO_INFO_FILE
    
    opts = [
        {'name':'path', 'help':'Path in the file-system to a server the service is deployed on'},
        {'name':'name', 'help':'Name of the service to invoke'},
        {'name':'--payload', 'help':'Payload to invoke the service with'},
        {'name':'--headers',
         'help':'Additional HTTP headers the service invoker will receive in format of header-name=header-value; header2-name=header2-value'},
        {'name':'--channel', 'help':'Channel the service will be invoked through', 'default':'invoke'},
        {'name':'--data-format', 'help':"Payload's data format", 'default': 'json'},
        {'name':'--transport', 'help':'Transport to invoke the service over'},
        {'name':'--url-path', 'help':'URL path zato.service.invoke is exposed on', 'default':'/zato/admin/invoke'},
        {'name':'--max-cid-repr',
         'help':'How many characters of each end of a CID to print out in verbose mode, defaults to {}, use {} to print the whole of it'.format(
            DEFAULT_MAX_CID_REPR, CID_NO_CLIP), 'default':DEFAULT_MAX_CID_REPR},
        {'name':'--max-response-repr', 'help':'How many characters of a response to print out in verbose mode, defaults to {}'.format(
            DEFAULT_MAX_RESPONSE_REPR), 'default':DEFAULT_MAX_RESPONSE_REPR},
        {'name':'--async', 'help':'If given, the service will be invoked asynchronously', 'action':'store_true'},
        {'name':'--expiration', 'help':'In async mode, after how many seconds the message should expire, defaults to {} seconds'.format(
            BROKER.DEFAULT_EXPIRATION), 'default':BROKER.DEFAULT_EXPIRATION},
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
                    
        client = AnyServiceInvoker(
            'http://{}'.format(config.main.gunicorn_bind), args.url_path, auth,
            max_response_repr=int(args.max_response_repr), max_cid_repr=int(args.max_cid_repr))
        
        # Prevents attempts to convert/escape XML into JSON
        to_json = True if args.data_format == DATA_FORMAT.JSON else False
        
        func = client.invoke_async if args.async else client.invoke
        response = func(args.name, args.payload, headers, args.channel, args.data_format, args.transport, to_json=to_json)
        
        if response.ok:
            self.logger.info(response.data or '(None)')
        else:
            self.logger.error(response.details)
            
        if args.verbose:
            self.logger.debug('inner.text:[{}]'.format(response.inner.text))
            self.logger.debug('response:[{}]'.format(response))
