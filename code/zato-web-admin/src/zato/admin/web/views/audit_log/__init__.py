# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The audit log page of the Dashboard, spread over one module per concern.

- columns - what each source's page looks like and the ceilings the page is bounded by
- sources - what one source can do with its own events
- query - reading one page of events and enriching it
- views - the views the page is served by
"""

# Zato
from zato.admin.web.views.audit_log.views import attachment_download, attachments, details, flow, journey, object_index, \
    poll, resubmit, strip

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'attachment_download',
    'attachments',
    'details',
    'flow',
    'journey',
    'object_index',
    'poll',
    'resubmit',
    'strip',
)

# ################################################################################################################################
# ################################################################################################################################
