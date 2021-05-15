# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import GENERIC
from zato.common.json_internal import loads
from zato.common.util.api import spawn_greenlet
from zato.server.service.internal.sso import BaseRESTService, BaseSIO
from zato.sso import status_code, ValidationError

# ################################################################################################################################

if 0:
    from zato.sso.common import SSOCtx

    SSOCtx = SSOCtx

# ################################################################################################################################
# ################################################################################################################################

class FlowPRT(BaseRESTService):
    """ Session manipulation through REST.
    """
    class SimpleIO:

        # Do not wrap elements in a top-level root element
        response_elem = None

        # Do not return keys that we have no values for
        skip_empty_keys = True

        # These elements are actually needed but we make them optional here to ensure
        # that SimpleIO does not raise any exceptions when they are not sent.
        input_optional = 'current_app', 'credential', 'token', 'reset_key'

        # Status will be always OK
        output_required = 'status', 'cid'

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        """ Creates a new PRT, assuming the incoming credential points to a valid user.
        """
        # type: (SSOCtx) -> None

        # Run asynchronously in a separate greenlet
        try:
            spawn_greenlet(self.sso.flow_prt.create_token, ctx)
        except Exception:
            # Log the exception but do not return it
            self.logger.warn('Exception in FlowPRT._handle_sso_POST `%s`', format_exc())

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx):
        """ Accesses a PRT, returning its access key on output.
        """

        self.sso.flow_prt.access(ctx)

        '''
        self.response.payload.expiration_time = self.sso.user.session.renew(self.cid, ctx.input.ust,
            ctx.input.current_app, ctx.remote_addr, self.wsgi_environ.get('HTTP_USER_AGENT')).isoformat()
        '''

# ################################################################################################################################
