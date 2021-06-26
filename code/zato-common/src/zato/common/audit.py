# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# ipaddress
from ipaddress import IPv4Address, IPv6Address

# Zato
from zato.common.json_internal import dumps

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class AuditPII(object):
    """ Audit log for personally identifiable information (PII).
    """
    def __init__(self):
        self._logger = logging.getLogger('zato_audit_pii')

# ################################################################################################################################

    def _log(self, func, cid, op, current_user='', target_user='', result='', extra='', _dumps=dumps):

        remote_addr = extra.get('remote_addr')

        if isinstance(extra, dict):
            if not remote_addr:
                extra['remote_addr'] = ''
            else:
                if isinstance(remote_addr, list) and remote_addr:
                    if isinstance(remote_addr[0], (IPv4Address, IPv6Address)):
                        extra['remote_addr'] = ';'.join(elem.exploded for elem in extra['remote_addr'])

        entry = {
            'cid': cid,
            'op': op,
        }

        if current_user:
            entry['current_user'] = current_user

        if target_user:
            entry['target_user'] = target_user

        if result:
            entry['result'] = result

        if extra:
            entry['extra'] = extra

        entry = dumps(entry)

        self._logger.info('%s' % entry)

# ################################################################################################################################

    def info(self, *args, **kwargs):
        self._log(self._logger.info, *args, **kwargs)

# ################################################################################################################################

    def warn(self, *args, **kwargs):
        self._log(self._logger.warn, *args, **kwargs)

# ################################################################################################################################

    def error(self, *args, **kwargs):
        self._log(self._logger.error, *args, **kwargs)

# ################################################################################################################################

# A singleton available everywhere
audit_pii = AuditPII()

# ################################################################################################################################
