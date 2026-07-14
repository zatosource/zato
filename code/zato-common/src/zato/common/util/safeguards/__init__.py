# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import SafeguardConfig, SafeguardResult, SafeguardSignal

# For flake8
apply_safeguards = apply_safeguards
SafeguardConfig = SafeguardConfig
SafeguardResult = SafeguardResult
SafeguardSignal = SafeguardSignal
