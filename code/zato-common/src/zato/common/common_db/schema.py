# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import BigInteger, Column, JSON, MetaData, PrimaryKeyConstraint, String, Table
from sqlalchemy.dialects.postgresql import JSONB

# Zato
from zato.common.db_env.common import Type_PostgreSQL, UTC_DateTime

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file of the common database.
common_db_file_name = 'common.db'

# Maximum length of the type and the name of a shared object.
_name_column_len = 200

# The documents of shared objects, binary JSON on PostgreSQL.
_data_type = JSON().with_variant(JSONB(), Type_PostgreSQL)

# ################################################################################################################################
# ################################################################################################################################

# All the tables of the common database.
metadata = MetaData()

# ################################################################################################################################

# One row per shared object - a JSON document under a type and a name, with the version that each write raises by one.
shared_object_table = Table('zato_shared_object', metadata,
    Column('object_type', String(_name_column_len), nullable=False),
    Column('name', String(_name_column_len), nullable=False),
    Column('data', _data_type, nullable=False),
    Column('version', BigInteger, nullable=False),
    Column('last_updated', UTC_DateTime, nullable=False),
    PrimaryKeyConstraint('object_type', 'name'),
)

# ################################################################################################################################
# ################################################################################################################################
