# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The extensions of pg8000, applied once per process when this module is imported. The engine module imports it
# before the first connection of pg8000 is opened, and the lock of the import system admits exactly one thread
# to its body.

# Zato
from zato.common.db_env.pg8000_copy import install as install_pg8000_copy
from zato.common.db_env.pg8000_wire import install as install_pg8000_wire

# ################################################################################################################################
# ################################################################################################################################

# The connections of PostgreSQL prepare their statements once and exchange bytea values and native types in the binary format,
# and they insert rows in bulk with COPY.
install_pg8000_wire()
install_pg8000_copy()

# ################################################################################################################################
# ################################################################################################################################
