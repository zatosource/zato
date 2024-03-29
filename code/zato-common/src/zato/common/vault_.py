# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
try:
    from zato.vault.client import VAULT

    # For pyflakes, otherwise it doesn't know that other parts of Zato import VAULT from here
    VAULT = VAULT
except ImportError:
    pass
