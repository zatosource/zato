# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import Lets_Encrypt
from zato.common.lets_encrypt.actions import check_port_now, enable_now, get_environ, get_public_endpoint, get_ssl_config, \
     set_lets_encrypt
from zato.common.util.api import spawn_greenlet
from zato.server.service import Bool
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

class Get(AdminService):
    """ Returns the certificate HAProxy presents, whether Let's Encrypt is enabled and the outcome of the most recent checks.
    """
    name = Lets_Encrypt.Service.Get

    def handle(self) -> 'None':

        environ = get_environ()

        self.response.payload = {'ssl_config': get_ssl_config(environ)}

# ################################################################################################################################
# ################################################################################################################################

class GetPublicEndpoint(AdminService):
    """ Returns the public IP address of this host and the DNS name it resolves back to, checked from the server itself.
    """
    name = Lets_Encrypt.Service.Get_Public_Endpoint

    def handle(self) -> 'None':

        environ = get_environ()

        self.response.payload = {'public_endpoint': get_public_endpoint(environ)}

# ################################################################################################################################
# ################################################################################################################################

class SetLetsEncrypt(AdminService):
    """ Enables or disables Let's Encrypt. Enabling it installs or obtains the certificate in the background,
    and the Dashboard follows each step of that through the next Gets.
    """
    name = Lets_Encrypt.Service.Set_Lets_Encrypt
    input = Bool('is_enabled')

    def handle(self) -> 'None':

        environ = get_environ()
        is_enabled = self.request.input.is_enabled

        set_lets_encrypt(environ, is_enabled)

        if is_enabled:
            _ = spawn_greenlet(enable_now, environ)

# ################################################################################################################################
# ################################################################################################################################

class CheckPort(AdminService):
    """ Checks in the background whether Let's Encrypt can reach this host through port 443,
    and the Dashboard learns how that went from the next Get.
    """
    name = Lets_Encrypt.Service.Check_Port

    def handle(self) -> 'None':

        environ = get_environ()

        _ = spawn_greenlet(check_port_now, environ)

# ################################################################################################################################
# ################################################################################################################################
