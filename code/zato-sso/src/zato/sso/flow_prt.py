# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger

# Zato
from zato.common import GENERIC
from zato.common.json_internal import json_dumps
from zato.common.odb.model import SSOFlowPRT as FlowPRTModel
from zato.sso import const, Default
from zato.sso.odb.query import get_user_by_email, get_user_by_name, get_user_by_name_or_email
from zato.sso.util import new_prt, new_prt_reset_key, new_user_session_token

# ################################################################################################################################

if 0:
    from typing import Callable
    from zato.common.odb.model import SSOUser
    from zato.server.base.parallel import ParallelServer
    from zato.sso.common import SSOCtx

    Callable = Callable
    ParallelServer = ParallelServer
    SSOCtx = SSOCtx
    SSOUser = SSOUser

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

FlowPRTModelTable = FlowPRTModel.__table__
FlowPRTModelInsert = FlowPRTModelTable.insert

# ################################################################################################################################
# ################################################################################################################################

# Maps configuration keys to functions that look up users in the database.
user_search_by_map = {
    'username':          get_user_by_name,
    'email':             get_user_by_email,
    'username_or_email': get_user_by_name_or_email,
}

# ################################################################################################################################
# ################################################################################################################################

class FlowPRTAPI(object):
    """ Message flow around password-reset tokens (PRT).
    """
    def __init__(self, server, sso_conf, odb_session_func):
        # type: (ParallelServer, dict, Callable) -> None
        self.server = server
        self.sso_conf = sso_conf
        self.odb_session_func = odb_session_func
        self.is_sqlite = None

        # PRT runtime configuration
        prt_config = sso_conf.get('prt', {}) # type: dict

        # For how long PRTs are valid (in seconds)
        valid_for = prt_config.get('valid_for')
        valid_for = valid_for or Default.prt_valid_for
        self.valid_for = int(valid_for)

        # For how long the one-off session to change the password will last (in minutes)
        duration = prt_config.get('password_change_session_duration')
        duration = duration or Default.prt_password_change_session_duration
        self.password_change_session_duration = int(duration)

        # By what credential to look up users in the database
        user_search_by = prt_config.get('user_search_by')
        user_search_by = user_search_by or Default.prt_user_search_by
        self.user_search_by_func = user_search_by_map[user_search_by]

# ################################################################################################################################

    def create_token(self, ctx, _utcnow=datetime.utcnow, _timedelta=timedelta):
        # type: (SSOCtx, object, object) -> None

        # Validate input
        if not ctx.input.credential:
            logger.warn('SSO credential missing on input to PRT:create_token (%s)', ctx.input)
            return

        # Look up the user in the database ..
        with closing(self.odb_session_func()) as session:
            user = self.user_search_by_func(session, ctx.input.credential) # type: SSOUser

            # .. make sure the user exists ..
            if not user:
                logger.warn('No such SSO user `%s` (%s)', ctx.input.credential, self.user_search_by_func)
                return

            # .. the user exists so we can now generate a new PRT ..
            prt = new_prt()

            # .. timestamp metadata ..
            creation_time = _utcnow()
            expiration_time = creation_time + timedelta(minutes=self.valid_for)

            # .. reset key used along with the PRT to reset the password ..
            reset_key = new_prt_reset_key()
            reset_key = self.server.encrypt(reset_key)

            # .. insert it into the database ..
            session.execute(
                FlowPRTModelInsert().values({
                    'creation_time': creation_time,
                    'expiration_time': expiration_time,
                    'user_id': user.user_id,
                    'value': prt,
                    'type_': const.prt.token_type,
                    'reset_key': reset_key,
                    GENERIC.ATTR_NAME: json_dumps(None)
            }))

            # .. commit the operation ..
            session.commit()

        # .. and notify the user.
        self.send_notification(user, prt)

# ################################################################################################################################

    def send_notification(self, user, prt):
        # type: (SSOUser, str)
        print()
        print(111, user)
        print(222, self.sso_conf.main.smtp_conn)
        print()

        if not self.sso_conf.main.smtp_conn:
            msg = 'Could not notify user `%s`, SSO SMTP connection not configured in sso.conf (main.smtp_conn)'
            logger.warn(msg, user.user_id)
            return
        else:
            zzz

# ################################################################################################################################

    def access(self, ctx, _utcnow=datetime.utcnow, _timedelta=timedelta):
        # type: (SSOCtx, object, object) -> str

        # MySQL does not support UPDATE .. RETURNING so we need to run the select query first
        # to get the PRT's access key and update it in another query.
        print()
        print(111, ctx)
        print()

# ################################################################################################################################

    def post_configure(self, func, is_sqlite):
        # type: (Callable, bool) -> None
        self.odb_session_func = func
        self.is_sqlite = is_sqlite

# ################################################################################################################################
# ################################################################################################################################