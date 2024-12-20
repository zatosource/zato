# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime

# ipaddress
from ipaddress import ip_address

# Zato
from zato.common.api import GENERIC
from zato.common.ext.dataclasses import dataclass, field
from zato.common.json_internal import dumps
from zato.common.odb.model import SSOSession as SessionModel
from zato.sso import const

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strnone
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

SessionModelTable = SessionModel.__table__
SessionModelInsert = SessionModelTable.insert

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class BaseRequestCtx:
    cid:             'str'
    remote_addr:     'str | strlist'
    user_agent:      'str'
    input:           'anydict'
    has_remote_addr: 'bool' = field(init=False, default=False)
    has_user_agent:  'bool' = field(init=False, default=False)

    def __post_init__(self) -> 'None':
        self.has_remote_addr = bool(self.input.get('remote_addr'))
        self.has_user_agent = bool(self.input.get('user_agent'))

        if isinstance(self.remote_addr, str):
            remote_addr = [elem.strip() for elem in self.remote_addr.strip().split(',')]
            remote_addr = [ip_address(elem) for elem in remote_addr]
            self.remote_addr = remote_addr

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class SSOCtx(BaseRequestCtx):
    """ A set of attributes describing current SSO request.
    """
    sso_conf: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class LoginCtx(BaseRequestCtx):
    """ A set of data about a login request.
    """
    ext_session_id: 'str' = field(init=False)

    def __post_init__(self) -> 'None':
        super().__post_init__()
        self.ext_session_id = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SessionInsertCtx:
    ust:             'str'
    creation_time:   'datetime'
    expiration_time: 'datetime'
    user_id:         'int'
    auth_type:       'str'
    auth_principal:  'str'
    remote_addr:     'str'
    user_agent:      'str'
    ctx_source:      'str'
    ext_session_id:  'strnone'
    interaction_max_len: 'int'

# ################################################################################################################################
# ################################################################################################################################

class VerifyCtx:
    """ Wraps information about a verification request.
    """
    __slots__ = ('ust', 'remote_addr', 'input', 'has_remote_addr', 'has_user_agent', 'current_app')

    def __init__(
        self,
        ust,         # type: str
        remote_addr, # type: str
        current_app, # type: str
        has_remote_addr=False, # type: bool
        has_user_agent=False   # type: bool
        ) -> 'None':

        self.ust = ust
        self.remote_addr = remote_addr
        self.has_remote_addr = has_remote_addr
        self.has_user_agent = has_user_agent
        self.current_app = current_app
        self.input = {
            'current_app': current_app
        }

# ################################################################################################################################
# ################################################################################################################################

def insert_sso_session(sql_session:'any_', insert_ctx:'SessionInsertCtx', needs_commit:'bool'=True) -> 'None':

    # Create current interaction details for this SSO session ..
    session_state_change_list = update_session_state_change_list(
        [],
        insert_ctx.interaction_max_len,
        insert_ctx.remote_addr,
        insert_ctx.user_agent,
        insert_ctx.ctx_source,
        insert_ctx.creation_time,
    )

    # .. convert interaction details into an opaque attribute ..
    opaque = dumps({
        'session_state_change_list': session_state_change_list
    })

    # .. run the SQL insert statement ..
    sql_session.execute(
        SessionModelInsert().values({
            'ust': insert_ctx.ust,
            'creation_time': insert_ctx.creation_time,
            'expiration_time': insert_ctx.expiration_time,
            'user_id': insert_ctx.user_id,
            'auth_type': insert_ctx.auth_type or const.auth_type.default,
            'auth_principal': insert_ctx.auth_principal,
            'remote_addr': ', '.join(str(elem) for elem in insert_ctx.remote_addr),
            'user_agent': insert_ctx.user_agent,
            'ext_session_id': insert_ctx.ext_session_id,
            GENERIC.ATTR_NAME: opaque
    }))

    # .. and commit the SQL state.
    if needs_commit:
        sql_session.commit()

# ################################################################################################################################
# ################################################################################################################################

def update_session_state_change_list(
    current_state,       # type: anylist
    interaction_max_len, # type: int
    remote_addr,         # type: str | anylist
    user_agent,          # type: str
    ctx_source,          # type: any_
    now                  # type: datetime
) -> 'None':
    """ Adds information about a user interaction with SSO, keeping the history
    of such interactions to up to max_len entries.
    """
    if current_state:
        idx = current_state[-1]['idx']
    else:
        idx = 0

    remote_addr = remote_addr if isinstance(remote_addr, list) else [remote_addr]

    if len(remote_addr) == 1:
        remote_addr = str(remote_addr[0])
    else:
        remote_addr = [str(elem) for elem in remote_addr]

    current_state.append({
        'remote_addr': remote_addr,
        'user_agent': user_agent,
        'timestamp_utc': now.isoformat(),
        'ctx_source': ctx_source,
        'idx': idx + 1
    })

    if len(current_state) > interaction_max_len:
        current_state.pop(0)

    return current_state

# ################################################################################################################################
