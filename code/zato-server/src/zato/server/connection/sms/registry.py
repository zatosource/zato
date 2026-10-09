# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Importing this module registers every provider class.

# Zato
from zato.server.connection.sms import africas_talking, infobip, twilio, vonage
from zato.server.connection.sms.base import get_all_provider_names, get_provider, get_provider_class

# ################################################################################################################################
# ################################################################################################################################

# Imported for registration
_provider_modules = (africas_talking, infobip, twilio, vonage)

__all__ = ['get_all_provider_names', 'get_provider', 'get_provider_class']

# ################################################################################################################################
# ################################################################################################################################
