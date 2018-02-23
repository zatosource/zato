# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

# SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, Sequence, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship

# ################################################################################################################################

class _SSOUser:
    __tablename__ = 'zato_sso_user'
    __table_args__ = (
        UniqueConstraint('username', name='zato_u_usrn_uq'),
        UniqueConstraint('user_id', name='zato_user_id_uq'),
        Index('zato_u_email_idx', 'email', unique=False, mysql_length={'email':767}),
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
    is_approved = Column(Boolean(), nullable=False, default=False)
    is_locked = Column(Boolean(), nullable=False, default=False)
    locked_time = Column(DateTime(), nullable=True)

    # Creation metadata, e.g. what this user's remote IP was
    creation_ctx = Column(Text(), nullable=False)

    # Note that this is not an FK - this is on purpose to keep this information around
    # even if parent row is deleted.
    locked_by = Column(String(191), nullable=True)

    approv_rej_time = Column(DateTime(), nullable=True) # When user was approved or rejected
    approv_rej_by = Column(String(191), nullable=True) # Same comment as in locked_by

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

# ################################################################################################################################

class _SSOSession:
    __tablename__ = 'zato_sso_session'
    __table_args__ = (
        Index('zato_sso_sust_idx', 'ust', unique=True),
    {})

    # Not exposed publicly, used only for SQL joins
    id = Column(Integer, Sequence('zato_sso_sid_seq'), primary_key=True)

    # Publicly visible session identifier (user session token)
    ust = Column(String(191), nullable=False)

    creation_time = Column(DateTime(), nullable=False)
    expiration_time = Column(DateTime(), nullable=False)

    remote_addr = Column(Text(), nullable=False)
    user_agent = Column(Text(), nullable=False)

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey('zato_sso_user.id', ondelete='CASCADE'), nullable=False)

# ################################################################################################################################
