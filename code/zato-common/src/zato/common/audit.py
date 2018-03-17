# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class AuditPII(object):
    """ Audit log for personally identifiable information (PII).
    """
    def __init__(self):
        self._logger = logging.getLogger('zato_audit_pii')

# ################################################################################################################################

    def info(self, cid, op, current_user='', target_user='', result='', extra=''):
        self._logger.info('%s,%s,%s,%s,%s,%s' % (cid, op, current_user, target_user, result, extra))

# ################################################################################################################################

    def warn(self, cid, op, current_user='', target_user='', result='', extra=''):
        self._logger.warn('%s,%s,%s,%s,%s,%s' % (cid, op, current_user, target_user, result, extra))

# ################################################################################################################################

    def error(self, cid, op, current_user='', target_user='', result='', extra=''):
        self._logger.error('%s,%s,%s,%s,%s,%s' % (cid, op, current_user, target_user, result, extra))

# ################################################################################################################################

# A singleton available everywhere
audit_pii = AuditPII()

# ################################################################################################################################
