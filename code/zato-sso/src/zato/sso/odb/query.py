# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import loads
from datetime import datetime

# SQLAlchemy
from sqlalchemy import or_

# Zato
from zato.common import GENERIC
from zato.common.odb.model import SSOLinkedAuth, SSOSession, SSOUser
from zato.common.util.sql import elems_with_opaque
from zato.sso import const

# ################################################################################################################################

_utcnow = datetime.utcnow

# ################################################################################################################################

_skip_user_columns = 'first_name_upper', 'middle_name_upper', 'last_name_upper', 'opaque1'
_skip_session_list_columns = 'id', 'user_id'

_user_id_column = [SSOUser.user_id]
_user_basic_columns = [elem for elem in SSOUser.__table__.c if elem.name not in _skip_user_columns]
_user_exists_columns = [SSOUser.user_id, SSOUser.username, SSOUser.email]

_session_columns = [elem for elem in SSOSession.__table__.c]
_session_list_columns = [elem for elem in SSOSession.__table__.c if elem.name not in _skip_session_list_columns]
_session_columns_with_user = _session_columns + _user_basic_columns

_approved = const.approval_status.approved

# ################################################################################################################################

def _session_with_opaque(session, _opaque_attr=GENERIC.ATTR_NAME):
    if session:
        opaque = getattr(session, GENERIC.ATTR_NAME, None)
        if opaque:
            opaque = loads(opaque)
            setattr(session, _opaque_attr, opaque)
    return session

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

def _get_model(session, columns):
    return session.query(*columns)

# ################################################################################################################################

def get_user_by_id(session, user_id, *ignored_args):
    return _get_model(session, _user_basic_columns).\
        filter(SSOUser.user_id==user_id).\
        first()

# ################################################################################################################################

def get_user_by_username(session, username, needs_approved=True, _approved=_approved):
    q = _get_model(session, _user_basic_columns).\
        filter(SSOUser.username==username)

    if needs_approved:
        q = q.filter(SSOUser.approval_status==_approved)

    return q.first()

# ################################################################################################################################

def _get_session(session, now, _columns=_session_columns_with_user, _approved=_approved):
    return _get_model(session, _columns).\
        filter(SSOSession.user_id==SSOUser.id).\
        filter(SSOUser.approval_status==_approved).\
        filter(SSOSession.expiration_time > now)

# ################################################################################################################################

def get_session_by_ext_id(session, ext_session_id, now):
    # type: (object, object, object) -> SSOSession
    session = _get_session(session, now).\
        filter(SSOSession.ext_session_id==ext_session_id).\
        first()

    return _session_with_opaque(session)

# ################################################################################################################################

def _get_session_by_ust(session, ust, now):
    return _get_session(session, now).\
        filter(SSOSession.ust==ust)

# ################################################################################################################################

def get_session_list_by_user_id(session, user_id, now, _columns=_session_list_columns):
    return elems_with_opaque(_get_session(session, now, _columns).\
           filter(SSOUser.user_id==user_id).\
           all())

# ################################################################################################################################

def get_session_by_ust(session, ust, now):
    session = _get_session_by_ust(session, ust, now).\
        first()

    return _session_with_opaque(session)

get_user_by_ust = get_session_by_ust

# ################################################################################################################################

def is_super_user_by_ust(session, ust, now=None):
    return _get_session_by_ust(session, ust, now or _utcnow(), _user_id_column).\
        filter(SSOUser.is_super_user==True).\
        first()

# ################################################################################################################################

def get_sign_up_status_by_token(session, confirm_token):
    return session.query(SSOUser.sign_up_status).\
        filter(SSOUser.sign_up_confirm_token==confirm_token).\
        first()

# ################################################################################################################################

def get_linked_auth_list(session, user_id=None):
    q = session.query(
        SSOLinkedAuth.user_id,
        SSOLinkedAuth.is_active,
        SSOLinkedAuth.is_internal,
        SSOLinkedAuth.creation_time,
        SSOLinkedAuth.has_ext_principal,
        SSOLinkedAuth.auth_type,
        SSOLinkedAuth.auth_id,
        SSOLinkedAuth.auth_principal,
        SSOLinkedAuth.auth_source,
        )

    if user_id:
        q = q.filter(SSOLinkedAuth.user_id==user_id)

    return q.all()

# ################################################################################################################################

def get_rate_limiting_info(session):
    return session.query(
        SSOUser.user_id,
        SSOUser.rate_limit_def
        ).\
        filter(SSOUser.is_rate_limit_active==True).\
        all()

# ################################################################################################################################
