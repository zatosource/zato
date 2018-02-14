# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import or_

# Zato
from zato.common.odb.model import SSOUser

# ################################################################################################################################

_skip_user_columns=('password',)
_user_basic_columns = [elem for elem in SSOUser.__table__.c if elem not in _skip_user_columns]
_user_exists_columns = [SSOUser.user_id, SSOUser.username, SSOUser.email]

# ################################################################################################################################

def user_exists(session, username, email):
    """ Returns a boolean flag indicating whether user exists by username or email.
    """
    return session.query(*_user_exists_columns).\
        filter(or_(
            SSOUser.username==username,
            SSOUser.email==email)
        ).\
        first()

# ################################################################################################################################
