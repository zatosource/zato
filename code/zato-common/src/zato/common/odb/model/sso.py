# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

# SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, Index, Integer, Sequence, String, UniqueConstraint

# ################################################################################################################################

class User:#(Base):
    __tablename__ = 'zato_sso_user'
    __table_args__ = (
        UniqueConstraint('cluster_id', 'username', name='zato_u_usrn_uq'),
        UniqueConstraint('cluster_id', 'pub_id', name='zato_u_pubid_uq'),
        Index('zato_u_email_idx', 'cluster_id', 'email', unique=False),
        Index('zato_u_dspn_idx', 'cluster_id', 'display_name_upper', unique=False),
        Index('zato_u_alln_idx', 'cluster_id', 'first_name_upper', 'middle_name_upper', 'last_name_upper',
              unique=False),
        Index('zato_u_lastn_idx', 'cluster_id', 'last_name_upper', unique=False),
    {})

    id = Column(Integer, Sequence('zato_user_id_seq'), primary_key=True)
    pub_id = Column(String(191), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False, default=False)

    # Basic information, always required
    username = Column(String(191), nullable=False)
    password = Column(String(191), nullable=False)
    password_is_set = Column(Boolean(), nullable=False)
    password_change = Column(Boolean(), nullable=False)
    password_expiry = Column(DateTime(), nullable=False)

    # Won't be always needed
    email = Column(String(191), nullable=True)

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

    #cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    #cluster = relationship(Cluster, backref=backref('user_list', order_by=username, cascade='all, delete, delete-orphan'))

# ################################################################################################################################
