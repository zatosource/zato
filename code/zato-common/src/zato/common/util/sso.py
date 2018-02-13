# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from uuid import uuid4

# Base32 Crockford
from base32_crockford import encode as crockford_encode

# Zato
from zato.common.util import new_cid

# ################################################################################################################################

def _new_id(prefix, _uuid4=uuid4, _crockford_encode=crockford_encode):
    return '%s%s' % (prefix, _crockford_encode(_uuid4().int).lower())

# ################################################################################################################################

def new_confirm_token(_new_id=_new_id):
    return _new_id('zcnt')

# ################################################################################################################################

def new_user_id(_new_id=_new_id):
    return _new_id('zust')

# ################################################################################################################################
