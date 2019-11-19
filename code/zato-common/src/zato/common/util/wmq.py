# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from binascii import unhexlify

# ################################################################################################################################

def unhexlify_wmq_id(wmq_id, _prefix='ID'):
    """ Converts the IBM MQ generated identifier back to bytes,
    e.g. 'ID:414d5120535052494e47505954484f4ecc90674a041f0020' -> 'AMQ SPRINGPYTHON\xcc\x90gJ\x04\x1f\x00 '.
    """
    return unhexlify(wmq_id.replace(_prefix, '', 1))

# ################################################################################################################################
