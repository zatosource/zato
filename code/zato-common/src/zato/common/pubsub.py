# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.util import new_cid

def new_msg_id(_new_cid=new_cid):
    return 'zpsm%s' % _new_cid()

def new_sub_key(_new_cid=new_cid):
    return 'zpsk%s' % _new_cid()

def new_group_id(_new_cid=new_cid):
    return 'zpsg%s' % _new_cid()
