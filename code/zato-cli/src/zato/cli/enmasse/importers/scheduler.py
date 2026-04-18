# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SchedulerImporter:

    scheduler_defaults = {
        'service': '',
        'job_type': 'interval_based',
        'is_active': True,
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.scheduler_defaults.items():
                if key not in item:
                    item[key] = default_value

            if 'name' in item:
                item['name'] = str(item['name'])

            if 'extra' in item:
                extra = item['extra']
                if isinstance(extra, dict):
                    raise ValueError(f'Scheduler job extra must be a list or string, got dict: {extra}')
                if isinstance(extra, list):
                    item['extra'] = '\n'.join(str(elem) for elem in extra if elem)

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
