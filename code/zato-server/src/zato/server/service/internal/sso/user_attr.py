# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal.sso.attr import _Attr, _AttrExists, _AttrNames

# ################################################################################################################################

class UserAttr(_Attr):
    pass

# ################################################################################################################################

class UserAttrExists(_AttrExists):
    pass

# ################################################################################################################################

class UserAttrNames(_AttrNames):
    pass

# ################################################################################################################################
