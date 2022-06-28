# -*- coding: utf-8 -*-

"""
Copyright (C) 202, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from cgi import FieldStorage
from io import BytesIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

def get_proxy_config(config):
    """ Returns HTTP/HTTPS proxy configuration from a given object's configuration data if any was configured.
    """
    # Proxy configuration, if any
    if config.http_proxy_list or config.https_proxy_list:
        proxy_config = {}

        # For now, all proxies we produce are not lists but a single one,
        # which can be revised if needed in the future.

        if config.http_proxy_list:
            proxy_config['http'] = config.http_proxy_list.strip()

        if config.https_proxy_list:
            proxy_config['https'] = config.https_proxy_list.strip()

        return proxy_config

# ################################################################################################################################

def get_form_data(wsgi_environ:'stranydict', as_dict:'bool'=True) -> 'stranydict':

    # Response to produce
    out = {}

    # This is the form data uploaded to a channel or service
    data = wsgi_environ['zato.http.raw_request'] # type: any_

    # Create a buffer to hold the form data and write the form to it
    buff = BytesIO()
    buff.write(data)
    buff.seek(0)

    # Output to return
    form = FieldStorage(fp=buff, environ=wsgi_environ, keep_blank_values=True)

    # Clean up
    buff.close()

    # Turn the FieldStorage object into a dict ..
    if as_dict:
        if form.list:
            form_to_dict = {item.name: item.value for item in form.list}
            out.update(form_to_dict)

    # Return the dict now
    return out

# ################################################################################################################################
