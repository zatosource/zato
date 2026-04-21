# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class ServiceConst:
    ServiceInvokerName = 'pub.zato.service.service-invoker'
    API_Admin_Invoke_Username = 'admin.invoke'
    API_Admin_Invoke_Url_Path = '/zato/admin/invoke'

# ################################################################################################################################
# ################################################################################################################################

class SECRETS:

    # These parameters will be automatically encrypted in SimpleIO input
    PARAMS = ('auth_data', 'auth_token', 'password', 'password1', 'password2', 'secret_key', 'token', 'secret')

    # Zato secret (Fernet)
    PREFIX = 'zato.secf.'
    PREFIX_BYTES = b'zato.secf.'

    # Encrypted data has this prefix
    Encrypted_Indicator = 'gAAA'

    # Zato secret (configuration)
    URL_PREFIX = 'zato+secret://'

# ################################################################################################################################
# ################################################################################################################################
