# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.common.util.api import spawn_greenlet
from zato.server.service.internal.sso import BaseRESTService, BaseSIO

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

        # These elements are actually needed but we make them optional here to ensure
        # that SimpleIO does not raise any exceptions when they are not sent.
        input_optional = 'current_app', 'credential', 'token', 'reset_key', 'password'

        output_required = 'status', 'cid'
        output_optional = BaseSIO.output_optional = ('reset_key',)

        # Do not wrap elements in a top-level root element
        response_elem = None

        # Do not return keys that we have no values for
        skip_empty_keys = True

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
        # Try to get a reset key for the input PRT ..
        reset_key = self.sso.flow_prt.access(ctx)

        # .. if we are here, it means that the PRT was accepted
        # and we can return the reset key to the client.
        self.response.payload.reset_key = reset_key

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx):
        """ Updates a password based on a PRT and reset key.
        """
        # Try to get a reset key for the input PRT and reset key ..
        reset_key = self.sso.flow_prt.change_password(ctx)

        # .. if we are here, it means that the PRT and reset key
        # were accepted, there is nothing else for us to do, we can return,
        # so let's be explicit about it.
        return

# ################################################################################################################################
