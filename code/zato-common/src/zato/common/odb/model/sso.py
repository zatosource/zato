# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, false as sa_false, ForeignKey, Index, Integer, Sequence, String, Text, \
     UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr

# Zato
from zato.common.odb.model.base import Base, _JSON

# ################################################################################################################################

class _SSOGroup(Base):
    __tablename__ = 'zato_sso_group'
    __table_args__ = (
        UniqueConstraint('name', 'source', name='zato_g_name_uq'),
        UniqueConstraint('group_id', name='zato_g_gid_uq'),
    {})

    # Not exposed publicly, used only for SQL joins
    id = Column(Integer, Sequence('zato_sso_group_id_seq'), primary_key=True)

    is_active = Column(Boolean(), nullable=False) # Currently unused and always set to True
    is_internal = Column(Boolean(), nullable=False, default=False)

    # Publicly visible
    group_id = Column(String(191), nullable=False)

    name = Column(String(191), nullable=False)
    source = Column(String(191), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    # Groups may be optionally nested
    parent_id = Column(Integer, ForeignKey('zato_sso_group.id', ondelete='CASCADE'), nullable=True)

# ################################################################################################################################

class _SSOUser(Base):
    __tablename__ = 'zato_sso_user'
    __table_args__ = (
        UniqueConstraint('username', name='zato_u_usrn_uq'),
        UniqueConstraint('user_id', name='zato_user_id_uq'),
        Index('zato_u_email_idx', 'email', unique=False, mysql_length={'email':767}),
        Index('zato_u_appr_stat_idx', 'approval_status', unique=False),
        Index('zato_u_dspn_idx', 'display_name_upper', unique=False),
        Index('zato_u_alln_idx', 'first_name_upper', 'middle_name_upper', 'last_name_upper', unique=False),
        Index('zato_u_lastn_idx', 'last_name_upper', unique=False),
        Index('zato_u_sigst_idx', 'sign_up_status', unique=False),
        Index('zato_u_sigctok_idx', 'sign_up_confirm_token', unique=True),
    {})

    # Not exposed publicly, used only for SQL joins
    id = Column(Integer, Sequence('zato_sso_user_id_seq'), primary_key=True)

    # Publicly visible
    user_id = Column(String(191), nullable=False)

    is_active = Column(Boolean(), nullable=False) # Currently unused and always set to True
    is_internal = Column(Boolean(), nullable=False, default=False)
    is_super_user = Column(Boolean(), nullable=False, default=False)
    is_locked = Column(Boolean(), nullable=False, default=False)
    locked_time = Column(DateTime(), nullable=True)

    # Creation metadata, e.g. what this user's remote IP was
    creation_ctx = Column(Text(), nullable=False)

    # Note that this is not an FK - this is on purpose to keep this information around
    # even if parent row is deleted.
    locked_by = Column(String(191), nullable=True)

    approval_status = Column(String(191), nullable=False)
    approval_status_mod_time = Column(DateTime(), nullable=False) # When user was approved or rejected
    approval_status_mod_by = Column(String(191), nullable=False) # Same comment as in locked_by

    # Basic information, always required
    username = Column(String(191), nullable=False)
    password = Column(Text(), nullable=False)
    password_is_set = Column(Boolean(), nullable=False)
    password_must_change = Column(Boolean(), nullable=False)
    password_last_set = Column(DateTime(), nullable=False)
    password_expiry = Column(DateTime(), nullable=False)

    # Sign-up information, possibly used in API workflows
    sign_up_status = Column(String(191), nullable=False)
    sign_up_time = Column(DateTime(), nullable=False)
    sign_up_confirm_time = Column(DateTime(), nullable=True)
    sign_up_confirm_token = Column(String(191), nullable=False)

    # Won't be always needed
    email = Column(Text(), nullable=True)

    # Various cultures don't have a notion of first or last name and display_name is the one that can be used in that case.
    display_name = Column(String(191), nullable=True)
    first_name = Column(String(191), nullable=True)
    middle_name = Column(String(191), nullable=True)
    last_name = Column(String(191), nullable=True)

    # Same as above but upper-cased for look-up / indexing purposes
    display_name_upper = Column(String(191), nullable=True)
    first_name_upper = Column(String(191), nullable=True)
    middle_name_upper = Column(String(191), nullable=True)
    last_name_upper = Column(String(191), nullable=True)

    # Rate limiting
    is_rate_limit_active = Column(Boolean(), nullable=True)
    rate_limit_type = Column(String(40), nullable=True)
    rate_limit_def = Column(Text(), nullable=True)
    rate_limit_check_parent_def = Column(Boolean(), nullable=True)

    # TOTP
    is_totp_enabled = Column(Boolean(), nullable=False, server_default=sa_false())
    totp_key = Column(Text(), nullable=True)
    totp_label = Column(Text(), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

# ################################################################################################################################

class _SSOUserGroup(Base):
    """ An N:N mapping of users to their groups.
    """
    __tablename__ = 'zato_sso_user_group'
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='zato_ug_id_uq'),
    {})

    # Not exposed publicly, used only to have a natural FK
    id = Column(Integer, Sequence('zato_sso_ug_seq'), primary_key=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    user_id = Column(Integer, ForeignKey('zato_sso_user.id', ondelete='CASCADE'), nullable=False)
    group_id = Column(Integer, ForeignKey('zato_sso_group.id', ondelete='CASCADE'), nullable=False)

# ################################################################################################################################

class _SSOSession(Base):
    __tablename__ = 'zato_sso_session'
    __table_args__ = (
        Index('zato_sso_sust_idx', 'ust', unique=True),
        Index('zato_sso_extsi_idx', 'ext_session_id', unique=False, mysql_length={'ext_session_id':767}),
    {})

    # Not exposed publicly, used only for SQL joins
    id = Column(Integer, Sequence('zato_sso_sid_seq'), primary_key=True)

    # Publicly visible session identifier (user session token)
    ust = Column(String(191), nullable=False)

    creation_time = Column(DateTime(), nullable=False)
    expiration_time = Column(DateTime(), nullable=False)

    remote_addr = Column(Text(), nullable=False)
    user_agent = Column(Text(), nullable=False)

    auth_type = Column(Text(), nullable=False)
    auth_principal = Column(Text(), nullable=False)

    # ID of a session external to SSO that is linked to this one,
    # where external may still mean JWT or Basic Auth,
    # but it is not a built-in SSO one.
    ext_session_id = Column(Text(), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey('zato_sso_user.id', ondelete='CASCADE'), nullable=False)

# ################################################################################################################################

class _SSOAttr(Base):
    __tablename__ = 'zato_sso_attr'

    __table_args__ = (
        UniqueConstraint('name', 'is_session_attr', 'user_id', '_ust_string', name='zato_attr_name_uq'),
        Index('zato_attr_usr', 'user_id', unique=False),
        Index('zato_attr_usr_ust', 'user_id', 'ust', unique=False),
        Index('zato_attr_usr_name', 'user_id', 'name', unique=False),
        Index('zato_attr_usr_ust_name', 'user_id', 'ust', 'name', unique=True),
    {})

    # Not exposed publicly, used only because SQLAlchemy requires an FK
    id = Column(Integer, Sequence('zato_sso_attr_seq'), primary_key=True)

    creation_time = Column(DateTime(), nullable=False)
    last_modified = Column(DateTime(), nullable=True)
    expiration_time = Column(DateTime(), nullable=True)

    is_session_attr = Column(Boolean(), nullable=False)
    is_encrypted = Column(Boolean(), nullable=False, default=False)
    serial_method = Column(String(20), nullable=False, default='json')

    name = Column(String(191), nullable=False)
    value = Column(Text(), nullable=True)

    # Unlike ust, this cannot be NULL so it may be used for practical purposes in the unique constraint 'zato_attr_name_uq',
    # otherwise all NULL values are considered different (or at least uncomparable) and API-wise, it is not possible
    # to construct a sensible unique constraint.
    _ust_string = Column(String(191), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    user_id = Column(String(191), ForeignKey('zato_sso_user.user_id', ondelete='CASCADE'), nullable=False)
    ust = Column(String(191), ForeignKey('zato_sso_session.ust', ondelete='CASCADE'), nullable=True)

# ################################################################################################################################

class _SSOLinkedAuth(Base):
    __tablename__ = 'zato_sso_linked_auth'

    __table_args__ = (
        Index('auth_idx', 'auth_type', 'user_id', 'auth_id', 'auth_principal', unique=True,
          mysql_length={'auth_type':191, 'user_id':191, 'auth_principal':191}),
    {})

    # Not exposed publicly, used only because SQLAlchemy requires an FK
    id = Column(Integer, Sequence('zato_sso_linked_auth_seq'), primary_key=True)

    is_active = Column(Boolean(), nullable=False) # Currently unused and always set to True
    is_internal = Column(Boolean(), nullable=False, default=False)

    creation_time = Column(DateTime(), nullable=False)
    last_modified = Column(DateTime(), nullable=True)

    # If True, auth_principal will point to an account/user defined externally to Zato,
    # e.g. in a system that Zato has no direct authentication support for.
    # Otherwise, if False, auth_id will be filled in.
    has_ext_principal = Column(Boolean(), nullable=False)

    # A label describing authentication type
    auth_type = Column(Text(191), nullable=False)

    #
    # Will be provided if has_ext_principal is False, in which case it will point to one of sec_base.id definitions.
    #
    # Note that if the SSO ODB is installed in a standalone database, this column will not be an FK
    # because there will be no parent sec_base.id column to point to. The Alembic logic to add
    # the FK after the table is created is implemented in cli/create_odb.py:Create.
    auth_id = Column(Integer, nullable=True)

    # Will be given if auth_id is not provided.
    auth_principal = Column(Text(191), nullable=True)

    # E.g. name of an environment this link is valid in - useful in cases when the same user
    # has multiple linked accounts, different in different auth sources (environments).
    auth_source = Column(Text(), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    # SSO user this entry links to
    user_id = Column(String(191), ForeignKey('zato_sso_user.user_id', ondelete='CASCADE'), nullable=False)

# ################################################################################################################################

class _SSOPasswordReset(Base):
    __tablename__ = 'zato_sso_password_reset'

    __table_args__ = (
        Index('zato_prt_value_type', 'token', 'type_', unique=True),
    {})

    # Not exposed publicly, used only because SQLAlchemy requires an FK
    id = Column(Integer, Sequence('zato_sso_flow_prt_seq'), primary_key=True)

    creation_time = Column(DateTime(), nullable=False)
    expiration_time = Column(DateTime(), nullable=False)

    # Creation metadata in JSON
    creation_ctx = Column(_JSON(), nullable=False)

    # The actual PRT (password reset token)
    token = Column(String(191), nullable=False)

    # PRT type - what kind is it of, e.g. a Zato built-in one or an external one?
    type_ = Column(String(191), nullable=False)

    # This key is used to reset the password after the PRT has been accessed
    reset_key = Column(String(191), nullable=False)

    # This is set when the PRT is accessed in order to set a time limit
    # for the password reset procedure (using prt.password_change_session_duration from sso.conf)
    reset_key_exp_time = Column(DateTime(), nullable=False)

    # Will be set to True when the PRT has been accessed in any way,
    # e.g. a user clicks on a link.
    has_been_accessed = Column(Boolean(), nullable=False, default=False)

    # When was the PRT accessed
    access_time = Column(DateTime(), nullable=True)

    # Access metadata in JSON
    access_ctx = Column(_JSON(), nullable=True)

    # Will be set to True when a password is reset using this PRT and reset_key
    is_password_reset = Column(Boolean(), nullable=False, default=False)

    # When was the password reset
    password_reset_time = Column(DateTime(), nullable=True)

    # Password reset metadata in JSON
    password_reset_ctx = Column(_JSON(), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    # SSO user this entry links to
    user_id = Column(String(191), ForeignKey('zato_sso_user.user_id', ondelete='CASCADE'), nullable=False)

# ################################################################################################################################
