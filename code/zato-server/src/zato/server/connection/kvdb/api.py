# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.connection.kvdb.core import ObjectCtx, KVDB
from zato.server.connection.kvdb.counter import CounterRepo
from zato.server.connection.kvdb.list_ import ListRepo

# For flake8
ObjectCtx = ObjectCtx
KVDB = KVDB
CounterRepo = CounterRepo
ListRepo = ListRepo
