# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The models that requests are built from and that responses are mapped to.

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.marshal_.api import Model

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Customer(Model):
    customer_id: 'int'
    name: 'str'

# ################################################################################################################################

@dataclass(init=False)
class Order(Model):
    order_id: 'int'
    customer: 'str'
    amount: 'float'

# ################################################################################################################################
# ################################################################################################################################
