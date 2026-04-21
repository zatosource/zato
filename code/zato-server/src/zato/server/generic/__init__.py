# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.util.api import get_sa_model_columns

# ################################################################################################################################

columns_gen_conn = set(get_sa_model_columns(ModelGenericConn))

attrs_gen_conn = set(columns_gen_conn)
attrs_gen_conn.remove(GENERIC.ATTR_NAME)
attrs_gen_conn.add('opaque')
attrs_gen_conn = tuple(attrs_gen_conn)

# ################################################################################################################################
