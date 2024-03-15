# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.connection.kvdb.core import ObjectCtx, KVDB
from zato.server.connection.kvdb.list_ import ListRepo
from zato.server.connection.kvdb.number import IntData, NumberRepo

# For flake8
IntData = IntData
KVDB = KVDB # type: ignore
ListRepo = ListRepo
NumberRepo = NumberRepo
ObjectCtx = ObjectCtx
