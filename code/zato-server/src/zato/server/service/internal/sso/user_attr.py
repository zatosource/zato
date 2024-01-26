# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal.sso.attr import _Attr, _AttrExists, _AttrNames

# ################################################################################################################################

class UserAttr(_Attr):
    _api_entity = 'user'

# ################################################################################################################################

class UserAttrExists(_AttrExists):
    _api_entity = 'user'

# ################################################################################################################################

class UserAttrNames(_AttrNames):
    _api_entity = 'user'

# ################################################################################################################################
