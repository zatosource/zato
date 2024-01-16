'''# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.api import Groups, Sec_Def_Type
from zato.common.crypto.api import is_string_equal
from zato.common.groups import Member
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dict_, intlist, intnone, intset, list_
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _BasicAuthSecDef:
    security_id: 'int'
    username: 'str'
    password: 'str'

# ################################################################################################################################
# ################################################################################################################################

class _APIKeySecDef:
    security_id: 'int'
    header_value: 'str'

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroupCtx:
    """ An instance of this class is attached to each channel using security groups.
    """

    # ID of a channel this ctx object is attached to
    channel_id: 'int'

    # IDs of all the security groups attached to this channel
    security_groups: 'intset'

    # Maps usernames to _BasicAuthSecDef objects
    basic_auth_credentials: 'dict_[str, _BasicAuthSecDef]'

    # Maps header values to _APIKeySecDef objects
    apikey_credentials: 'dict_[str, _APIKeySecDef]'

    def __init__(self) -> 'None':

        security_groups:'intset' = set()
        self.basic_auth_credentials = {}
        self.apikey_credentials = {}

        self._lock = RLock()

# ################################################################################################################################

    def check_security_basic_auth(self, cid:'str', channel_name:'str', username:'str', password:'str') -> 'intnone':

        if sec_info := self.basic_auth_credentials.get(username):
            if is_string_equal(password, sec_info.password):
                return sec_info.security_id
            else:
                logger.info(f'Invalid password; username={username}; channel={channel_name}; cid={cid}')
        else:
            logger.info(f'Username not found; username={username}; channel={channel_name}; cid={cid}')

# ################################################################################################################################

    def _get_basic_auth_by_security_id(self, security_id:'int') -> '_BasicAuthSecDef | None':

        for value in self.basic_auth_credentials.values():
            if value.security_id == security_id:
                return value

# ################################################################################################################################

    def _create_basic_auth(
        self,
        group_id:'int',
        member_id:'int',
        security_id:'int',
        username:'str',
        password:'str'
    ) -> 'None':

        # Build a business object containing all the data needed in runtime ..
        item = _BasicAuthSecDef()
        item.security_id = security_id
        item.username = username
        item.password = password

        # .. and add the business object to our container.
        self.basic_auth_credentials[username] = item

# ################################################################################################################################

    def _create_apikey(
        self,
        group_id:'int',
        member_id:'int',
        security_id:'int',
        header_value:'str',
    ) -> 'None':

        # .. build a business object containing all the data needed in runtime ..
        item = _APIKeySecDef()
        item.security_id = security_id
        item.header_value = header_value

        # .. add the business object to our container.
        self.apikey_credentials[item.header_value] = item

# ################################################################################################################################

    def edit_basic_auth(self, security_id:'int', current_username:'str', password:'str') -> 'None':

        with self._lock:
            if sec_info := self._get_basic_auth_by_security_id(security_id):
                _ = self.basic_auth_credentials.pop(sec_info.username)

# ################################################################################################################################

    def delete_basic_auth(self, security_id:'int') -> 'None':
        with self._lock:
            pass

# ################################################################################################################################

    def check_security_apikey(self, cid:'str', channel_name:'str', header_value:'str') -> 'intnone':

        if sec_info := self.apikey_credentials.get(header_value):
            return sec_info.security_id
        else:
            logger.info(f'Invalid API key; channel={channel_name}; cid={cid}')

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroupCtxBuilder:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server
        self.members = self.server.groups_manager.get_member_list(Groups.Type.API_Clients)

# ################################################################################################################################

    def _get_members_by_group_id(self, group_id:'int') -> 'list_[Member]':

        # Our response to produce
        out:'list_[Member]' = []

        # Go through each of the members that we are aware of ..
        for item in self.members:

            # .. check if the member belongs to our input group ..
            if item.group_id == group_id:

                # .. if yes, add it to our output ..
                out.append(item)

        # .. finally, we can return the response to our caller.
        return out

# ################################################################################################################################

    def build_ctx(self, channel_id:'int', security_groups: 'intlist') -> 'SecurityGroupCtx':

        # Build a basic object ..
        ctx = SecurityGroupCtx()

        # .. populate it with the core data ..
        ctx.channel_id = channel_id
        ctx.security_groups = set(security_groups)

        # .. add all the credentials ..
        for group_id in ctx.security_groups:

            # .. first, add an indication that we use this group,
            # .. no matter what members are in it ..
            ctx.security_groups.add(group_id)

            # .. next, extract all the members from this group ..
            members = self._get_members_by_group_id(group_id)

            # .. now, go through each of the members found ..
            for member in members:

                # .. and add it to a container corresponding to its security type ..
                if member.sec_type == Sec_Def_Type.BASIC_AUTH:

                    # .. get the member's security definition ..
                    sec_def = self.server.worker_store.basic_auth_get_by_id(member.security_id)

                    # .. populate the correct container ..
                    ctx._create_basic_auth(
                        group_id,
                        member.id,
                        sec_def['id'],
                        sec_def['username'],
                        sec_def['password'],
                    )

                elif member.sec_type == Sec_Def_Type.APIKEY:

                    # .. get the member's security definition ..
                    sec_def = self.server.worker_store.apikey_get_by_id(member.security_id)

                    # .. populate the correct container ..
                    ctx._create_apikey(
                        group_id,
                        member.id,
                        sec_def['id'],
                        sec_def['password'],
                    )

        # .. and return the business object to our caller.
        return ctx

# ################################################################################################################################
# ################################################################################################################################

class BuildCtx(Service):
    name = 'dev.groups.build-ctx'

    def handle(self):

        channel_id = 85
        security_groups = [1, 3]

        builder = SecurityGroupCtxBuilder(self.server)
        ctx = builder.build_ctx(channel_id, security_groups)

        cid = 'cid.1'
        channel_name = 'channel.1'

        result = ctx.check_security_basic_auth(cid, channel_name, '111', '111')
        print('QQQ-1', result)

        result = ctx.check_security_apikey(cid, channel_name, '222')
        print('QQQ-2', result)

# ################################################################################################################################
# ################################################################################################################################
'''
