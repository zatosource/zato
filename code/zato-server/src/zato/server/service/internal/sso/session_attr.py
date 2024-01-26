# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal.sso.attr import _Attr, _AttrExists, _AttrNames

# ################################################################################################################################

class SessionAttr(_Attr):
    _api_entity = 'session'

# ################################################################################################################################

class SessionAttrExists(_AttrExists):
    _api_entity = 'session'

# ################################################################################################################################

class SessionAttrNames(_AttrNames):
    _api_entity = 'session'

# ################################################################################################################################
