# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from traceback import format_exc

# Zato
from zato.common.util.api import spawn_greenlet
from zato.common.odb.model import SSOUser as UserModel
from zato.server.service import List, Service
from zato.server.service.internal.sso import BaseRESTService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.sso.common import SSOCtx
    SSOCtx = SSOCtx

# ################################################################################################################################
# ################################################################################################################################

UserModelTable = UserModel.__table__
UserModelTableSelect = UserModelTable.select

# ################################################################################################################################
# ################################################################################################################################

class PasswordReset(BaseRESTService):
    """ Session manipulation through REST.
    """
    class SimpleIO:

        # These elements are actually needed but we make them optional here to ensure
        # that SimpleIO does not raise any exceptions when they are not sent.
        input_optional = 'current_app', 'credential', 'token', 'reset_key', 'password'

        output_required = 'status', 'cid'
        output_optional = ('reset_key', List('sub_status'))

        # Do not wrap elements in a top-level root element
        response_elem = None

        # Do not return keys that we have no values for
        skip_empty_keys = True

# ################################################################################################################################

    def _handle_sso_POST(self, ctx:'SSOCtx') -> 'None':
        """ Creates a new PRT, assuming the incoming credential points to a valid user.
        """
        # Run asynchronously in a separate greenlet
        try:
            _ = spawn_greenlet(
                self.sso.password_reset.create_token,
                self.cid,
                ctx.input.credential,
                ctx.input.current_app,
                ctx.remote_addr,
                ctx.user_agent
            )
        except Exception:
            # Log the exception but do not return it
            self.logger.warning('Exception in FlowPRT._handle_sso_POST `%s`', format_exc())

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx:'SSOCtx') -> 'None':
        """ Accesses a PRT, returning its access key on output.
        """
        # This will be encrypted by SIO
        ctx.input.token = self.server.decrypt(ctx.input.token)

        # Try to get a reset key for the input PRT ..
        access_token_ctx = self.sso.password_reset.access_token(
            self.cid, ctx.input.token, ctx.input.current_app, ctx.remote_addr, ctx.user_agent)

        # .. if we are here, it means that the PRT was accepted
        # and we can return the reset key to the client.
        self.response.payload.reset_key = access_token_ctx.reset_key

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx:'SSOCtx') -> 'None':
        """ Updates a password based on a PRT and reset key.
        """
        # This will be encrypted by SIO
        ctx.input.token = self.server.decrypt(ctx.input.token)
        ctx.input.password = self.server.decrypt(ctx.input.password)

        # Try to get a reset key for the input PRT and reset key ..
        self.sso.password_reset.change_password(
            self.cid, ctx.input.password, ctx.input.token, ctx.input.reset_key,
            ctx.input.current_app, ctx.remote_addr, ctx.user_agent)

        # .. if we are here, it means that the PRT and reset key
        # were accepted, there is nothing else for us to do, we can return,
        # so let's be explicit about it.
        return

# ################################################################################################################################
# ################################################################################################################################

class PasswordExpiryHandler(Service):
    name = 'pub.zato.sso.password-expiry.handler'

    def handle(self) -> 'None':

        # We need to be invoked with a service that will process any users that find.
        # Without this service, we cannot continue.
        raw = self.request.raw_request
        is_dict_no_input = isinstance(raw, dict) and len(raw) == 1 and 'skip_response_elem' in raw
        if (not raw) or is_dict_no_input:
            self.logger.info('Service `%s` needs to be invoked with a processor service on input', self.name)
            return
        else:
            processor_service = self.request.raw_request
            self.logger.info('Running `%s` with a processor service on input -> `%s`', self.name, processor_service)

        # Local aliases
        now = datetime.utcnow()
        sso_conf = self.sso.sso_conf
        to_process = []

        # We look up users in the SSO database
        select = UserModelTableSelect()

        # Get all the users - processing them in Python is the most cross-platform way
        query = select.\
            with_only_columns((
                UserModelTable.c.username,
                UserModelTable.c.email,
                UserModelTable.c.display_name,
                UserModelTable.c.password_expiry,
            )).\
            where(UserModelTable.c.is_locked.is_(False)).\
            order_by(UserModelTable.c.username)

        # Obtain a new SQL session ..
        with closing(self.odb.session()) as session:

            # .. run the query ..
            result = session.execute(query)

            # .. go through each of the users ..
            for item in result:

                # .. build a threshold time specific to each user ..
                threshold_time = item.password_expiry - timedelta(days=sso_conf.password.about_to_expire_threshold)

                # .. if it has been reached ..
                if now > threshold_time:

                    # .. transform the item to a Python dict ..
                    item_as_dict = dict(item.items())

                    # .. add flags indicating whether the password has already expired or it is about to ..
                    item_as_dict['is_password_expired']         = item_as_dict['password_expiry'] < now
                    item_as_dict['is_password_about_to_expire'] = item_as_dict['password_expiry'] > now

                    # .. append the user to the list of users to process ..
                    to_process.append(item_as_dict)

        if to_process:
            self.logger.info('Sending %s result(s) to service `%s`', len(to_process), processor_service)
            self.invoke(processor_service, to_process)
        else:
            self.logger.info('No results to send to service `%s`', processor_service)

# ################################################################################################################################
# ################################################################################################################################
