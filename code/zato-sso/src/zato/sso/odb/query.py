# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime

# Bunch
from bunch import bunchify

# SQLAlchemy
from sqlalchemy import or_

# Zato
from zato.common.api import GENERIC
from zato.common.json_internal import loads
from zato.common.odb.model import SecurityBase, SSOPasswordReset, SSOLinkedAuth, SSOSession, SSOUser
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
        opaque = getattr(session, _opaque_attr, None)
        if opaque:
            opaque = loads(opaque)
            session = session._asdict()
            session[_opaque_attr] = opaque
            return bunchify(session)
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

def _get_user_base_query(session, needs_approved=True, _approved=_approved):
    q = _get_model(session, _user_basic_columns)

    if needs_approved:
        q = q.filter(SSOUser.approval_status==_approved)

    return q

# ################################################################################################################################

def get_user_by_name(session, username, needs_approved=True):

    # Get the base query ..
    q = _get_user_base_query(session, needs_approved)

    # .. filter by username ..
    q = q.filter(SSOUser.username==username)

    # .. and return the result.
    return q.first()

# ################################################################################################################################

def get_user_by_email(session, email, needs_approved=True):

    # Get the base query ..
    q = _get_user_base_query(session, needs_approved)

    # .. filter by email ..
    q = q.filter(SSOUser.email==email)

    # .. and return the result.
    return q.first()

# ################################################################################################################################

def get_user_by_name_or_email(session, credential, needs_approved=True):

    # Get the base query ..
    q = _get_user_base_query(session, needs_approved)

    # .. filter by username or email..
    q = q.filter(or_(
        SSOUser.username==credential,
        SSOUser.email==credential,
    ))

    # .. and return the result.
    return q.first()

# ################################################################################################################################

def _get_user_by_prt(session, prt, now):

    # Get the base query ..
    return session.query(
        SSOUser.user_id,
        SSOUser.password_expiry,
        SSOUser.username,
        SSOUser.is_locked,
        SSOUser.sign_up_status,
        SSOUser.approval_status,
        SSOUser.password_expiry,
        SSOUser.password_must_change,
        SSOPasswordReset.reset_key,
        ).\
        filter(SSOPasswordReset.token == prt).\
        filter(SSOUser.user_id == SSOPasswordReset.user_id).\
        filter(SSOPasswordReset.expiration_time > now).\
        filter(SSOPasswordReset.reset_key_exp_time > now)

# ################################################################################################################################

def get_user_by_prt(session, prt, now):

    # Get the base query ..
    q = _get_user_by_prt(session, prt, now)

    # .. at this point, the password is still not reset
    # and we need to ensure that the PRT has not been accessed either ..
    q = q.\
        filter(SSOPasswordReset.has_been_accessed.is_(False)).\
        filter(SSOPasswordReset.is_password_reset.is_(False))

    # .. and return the result.
    return q.first()

# ################################################################################################################################

def get_user_by_prt_and_reset_key(session, prt, reset_key, now):

    # Get the base query ..
    q = _get_user_by_prt(session, prt, now)

    q = q.\
        filter(SSOPasswordReset.reset_key == reset_key).\
        filter(SSOPasswordReset.has_been_accessed.is_(True)).\
        filter(SSOPasswordReset.is_password_reset.is_(False))

    # .. and return the result.
    return q.first()

# ################################################################################################################################

def get_user_by_linked_sec(session, query_criteria, *ignored_args):
    auth_type, auth_name = query_criteria
    q = session.query(
        *_user_basic_columns
    ).\
    filter(SSOUser.user_id==SSOLinkedAuth.user_id).\
    filter(SSOLinkedAuth.auth_type=='zato.{}'.format(auth_type)).\
    filter(SecurityBase.name==auth_name).\
    filter(SecurityBase.id==SSOLinkedAuth.auth_id)

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
    result = _get_session(session, now).\
        filter(SSOSession.ext_session_id==ext_session_id).\
        first()

    return _session_with_opaque(result)

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
        first() # noqa: E712

# ################################################################################################################################

def get_sign_up_status_by_token(session, confirm_token):
    return session.query(SSOUser.sign_up_status).\
        filter(SSOUser.sign_up_confirm_token==confirm_token).\
        first()

# ################################################################################################################################

def get_linked_auth_list(session, user_id=None, auth_id=None):
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

    if auth_id:
        q = q.filter(SSOLinkedAuth.auth_id==auth_id)

    return q.all()

# ################################################################################################################################

def get_rate_limiting_info(session):
    return session.query(
        SSOUser.user_id,
        SSOUser.rate_limit_def
        ).\
        filter(SSOUser.is_rate_limit_active==True).\
        all() # noqa: E712

# ################################################################################################################################
