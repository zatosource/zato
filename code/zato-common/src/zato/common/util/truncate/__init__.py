# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.truncate.api import truncate_json
from zato.common.util.truncate.common import DropReportEntry, TruncateResult

# For flake8
truncate_json = truncate_json
DropReportEntry = DropReportEntry
TruncateResult = TruncateResult
