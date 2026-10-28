# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import stranydict
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The prefix of the environment variables the audit log database is configured through.
Env_Prefix = 'Zato_Audit_Log_DB_'

Type_MySQL      = 'mysql'
Type_PostgreSQL = 'postgresql'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PerfDatabase:
    """ One database a performance test runs against.
    """
    name: str
    engine: 'Engine'

    # The environment variables the host process connects to the database with.
    env: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################
