# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json
import pkg_resources
import re

# Paste
from paste.util.converters import asbool

# Zato
from zato.common.match import Matcher
from zato.common.util import get_brython_js
from zato.server.connection.http_soap import NotFound
from zato.server.service import Service

# ################################################################################################################################

class _Base(Service):

    def validate_input(self):
        if not asbool(self.server.fs_server_config.apispec.pub_enabled):

            # Note that we are using the same format that regular 404 does
            raise NotFound(self.cid, '[{}] Unknown URL:[{}] or SOAP action:[]'.format(
                self.cid, self.wsgi_environ['zato.channel_item']['url_path']))

# ################################################################################################################################

class Main(_Base):
    """ Returns public version of API specifications.
    """
    def filter_services(self, matcher, services):
        return [svc for svc in services if matcher.is_allowed(svc['name'])]

# ################################################################################################################################

    def get_filtered_apispec_response(self):
        """Return zato.apispec.get-api-spec response filtered according to apispec_services_allowed config."""
        matcher = Matcher()
        matcher.read_config(self.server.fs_server_config.apispec_services_allowed)

        response = json.loads(self.invoke('zato.apispec.get-api-spec', {'return_internal': True}))
        response['services'] = self.filter_services(matcher, response['services'])

        # Remove any namespace definitions for which no service matched.
        for namespace, info in list(response['namespaces'].items()):
            info['services'] = self.filter_services(matcher, info['services'])
            if not info['services']:
                del response['namespaces'][namespace]

        return json.dumps(response)

# ################################################################################################################################

    def handle(self):
        replace_with = {
            'ZATO_BASE_CSS': pkg_resources.resource_string(__name__, 'data/style.css').decode('utf-8'),
            'ZATO_CLUSTER_ID': str(self.server.cluster_id),
            'ZATO_DATA': self.get_filtered_apispec_response(),
            'ZATO_LOGO': pkg_resources.resource_string(__name__, 'data/logo.png').encode('base64'),
            'ZATO_PUB_CSS_STYLE': self.server.fs_server_config.apispec.pub_css_style,
            'ZATO_PUB_NAME': self.server.fs_server_config.apispec.pub_name,
        }

        page_template = pkg_resources.resource_string(__name__, 'data/index.html').decode('utf-8')
        replace = lambda match: replace_with[match.group(1)]
        self.response.payload = re.sub('{{([^}]+)}}', replace, page_template)
        self.response.headers['Content-Type'] = 'text/html'

# ################################################################################################################################

class BrythonJS(_Base):
    """ Returns Brython's main source code module.
    """
    def handle(self):
        self.response.payload = get_brython_js()
        self.response.headers['Content-Type'] = 'text/javascript'

# ################################################################################################################################

class BrythonJSON(_Base):
    """ Brython's 'json' module.
    """
    def handle(self):
        _json = """var $module = (function($B){

return  {
    loads : function(json_obj){
        return $B.jsobject2pyobject(JSON.parse(json_obj))
    },
    load : function(file_obj){
        return $module.loads(file_obj.$content);
    },
    dumps : function(obj){return JSON.stringify($B.pyobject2jsobject(obj))},
}

})(__BRYTHON__)
"""
        self.response.payload = _json
        self.response.headers['Content-Type'] = 'text/javascript'

# ################################################################################################################################

class Frontend(_Base):
    """ Returns Brython frontend code to display API specifications.
    """
    def handle(self):
        self.response.payload = pkg_resources.resource_string(__name__, 'data/docs.py')
        self.response.headers['Content-Type'] = 'text/python'

# ################################################################################################################################

class GetDefaultAuthType(Service):
    """ Returns default authentication method to use for clients (browsers) accessing public API specifications.
    """
    class SimpleIO:
        output_required = ('auth_type',)

    def handle(self):
        self.response.payload.auth_type = 'Basic realm="{}"'.format(self.server.fs_server_config.apispec.pub_name)


'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Bunch
from bunch import bunchify

# Zato
from zato.server.apispec.wsdl import WSDLGenerator
from zato.server.service import Opaque, Service

# ################################################################################################################################

class GetSphinx(Service):
    name = 'apispec.get-sphinx'

    class SimpleIO:
        input_required = Opaque('data'),
        output_required = Opaque('data'),

# ################################################################################################################################

    def add_default_files(self, files):
        """ Returns default static files that always exist.
        """ 
        apispec_dir = os.path.join(self.server.static_dir, 'sphinxdoc', 'apispec')
        for dir_path, dir_names, file_names in os.walk(apispec_dir):
            if dir_path == apispec_dir:
                base_dir = '.'
            else:
                base_dir = os.path.basename(dir_path)

            for file_name in file_names:
                relative_path = os.path.join(base_dir, file_name)

                f = open(os.path.join(dir_path, file_name))
                contents = f.read()
                f.close()

                files[relative_path] = contents

# ################################################################################################################################

    def get_wsdl(self, data):
        services = bunchify(data['services'])
        target_ns = 'urn:zato-apispec'
        return WSDLGenerator(services, target_ns).generate()

# ################################################################################################################################

    def add_services(self, data, files):
        for elem in data.services:
            name = elem.name
            ns = elem.namespace_name
            docs = elem.docs
            sio = elem.simple_io
            print(111, `ns`, name, sio)

# ################################################################################################################################

    def handle(self):
        data = bunchify(self.request.input.data)
        files = {}

        self.add_default_files(files)
        self.add_services(data, files)
        files['download/api.wsdl'] = self.get_wsdl(data)

        self.response.payload.data = files
        
# ################################################################################################################################
'''
