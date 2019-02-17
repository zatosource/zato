# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.odb.model import SSOAttr, SSOSession
from zato.server.service import Service

# ################################################################################################################################

class Cleanup(Service):
    """ Cleans up expired SSO objects, such as sessions or attributes.
    """
    def handle(self):
        sleep_time = int(self.request.raw_request)

        if not self.server.is_sso_enabled:
            self.logger.info('SSO not enabled, cleanup task skipped')
            return

        while True:
            try:
                sleep(sleep_time)

                with closing(self.odb.session()) as session:

                    # Get current time
                    now = datetime.utcnow()

                    # Clean up expired sessions
                    self._cleanup_sessions(session, now)

                    # Clean up expired attributes
                    self._cleanup_attrs(session, now)

                    # Commit all deletes
                    session.commit()

            except Exception:
                self.logger.warn('Error in SSO cleanup: `%s`', format_exc())
                sleep(sleep_time)
            else:
                self.logger.info('SSO cleanup completed successfully')

# ################################################################################################################################

    def _cleanup_sessions(self, session, now):
        return session.query(SSOSession).\
            filter(SSOSession.expiration_time <= now).\
            delete()

# ################################################################################################################################

    def _cleanup_attrs(self, session, now):
        return session.query(SSOAttr).\
            filter(SSOAttr.expiration_time <= now).\
            delete()

# ################################################################################################################################
