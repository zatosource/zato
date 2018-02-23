# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime

# SQLAlchemy
from sqlalchemy import or_

# Zato
from zato.common.odb.model import SSOSession, SSOUser

# ################################################################################################################################

_skip_user_columns=('password',)
_user_basic_columns = [elem for elem in SSOUser.__table__.c if elem not in _skip_user_columns]
_user_exists_columns = [SSOUser.user_id, SSOUser.username, SSOUser.email]
_session_columns = [elem for elem in SSOSession.__table__.c]
_session_columns_with_user = _session_columns + _user_basic_columns

# ################################################################################################################################

def user_exists(session, username, email, check_email):
    """ Returns a boolean flag indicating whether user exists by username or email.
    """
    if check_email:
        condition = or_(SSOUser.username==username, SSOUser.email==email)
    else:
        condition = SSOUser.username==username

    return session.query(*_user_exists_columns).\
        filter(condition).\
        first()

# ################################################################################################################################

def _get_user(session, columns):
    return session.query(*columns)

# ################################################################################################################################

def get_user_by_id(session, user_id):
    return _get_user(session, _user_basic_columns).\
        filter(SSOUser.user_id==user_id).\
        first()

# ################################################################################################################################

def get_user_by_username(session, username):
    return _get_user(session, _user_basic_columns).\
        filter(SSOUser.username==username).\
        first()

# ################################################################################################################################

def get_session_by_ust(session, ust, now):
    return _get_user(session, _session_columns_with_user).\
        filter(SSOSession.user_id==SSOUser.id).\
        filter(SSOSession.ust==ust).\
        filter(SSOSession.expiration_time > now).\
        first()

# ################################################################################################################################

def is_super_user_by_user_id(session, user_id):
    raise NotImplementedError()

# ################################################################################################################################

def is_super_user_by_ust(session, ust):
    raise NotImplementedError()

# ################################################################################################################################
