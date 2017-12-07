# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# pkg_resources
import pkg_resources

# Paste
from paste.util.converters import asbool

# Zato
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
    def handle(self):

        replace_with = {
            'ZATO_DATA': self.invoke('zato.apispec.get-api-spec'),
            'ZATO_LOGO': pkg_resources.resource_string(__name__, 'data/logo.png').encode('base64'),
            'ZATO_CLUSTER_ID': str(self.server.cluster_id),
            'ZATO_PUB_NAME': self.server.fs_server_config.apispec.pub_name,
            'ZATO_PUB_CSS_STYLE': self.server.fs_server_config.apispec.pub_css_style,
        }

        page_template = pkg_resources.resource_string(__name__, 'data/index.html').decode('utf-8')
        for k, v in replace_with.items():
            page_template = page_template.replace(k, v)

        self.response.payload = page_template
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
