# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy 1.4 knows Oracle only through the cx_Oracle driver, so python-oracledb
# is made importable under that name, which is the arrangement python-oracledb documents
# for SQLAlchemy 1.4. This module must be imported before the first oracle:// engine
# is created, which is why the modules that build SQL engines import it themselves.
#
# The driver stays in thin mode - nothing here or anywhere else may call
# oracledb.init_oracle_client, because thin mode does its network I/O through Python's
# own socket module, which is what makes Oracle queries cooperative under gevent.

# stdlib
import sys

# oracledb
import oracledb

# ################################################################################################################################
# ################################################################################################################################

# The version the cx_Oracle dialect's minimum-version check parses - this is
# the last cx_Oracle release, the one that python-oracledb replaced.
oracledb.version = '8.3.0'

sys.modules['cx_Oracle'] = oracledb

# ################################################################################################################################
# ################################################################################################################################
