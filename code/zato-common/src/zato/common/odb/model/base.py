# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# dictalchemy
from dictalchemy import make_class_dictable

# SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

# ################################################################################################################################

Base = declarative_base()
make_class_dictable(Base)

# ################################################################################################################################
