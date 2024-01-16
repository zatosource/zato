# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent.lock import RLock

# Zato
from zato.common.api import Groups, Sec_Def_Type
from zato.common.groups import Member
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, intset, list_, strdict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class _BasicAuthSecDef:

    group_id: 'int'
    member_id: 'int'
    security_id: 'int'
    password: 'str'

# ################################################################################################################################
# ################################################################################################################################

class _APIKeySecDef:

    group_id: 'int'
    member_id: 'int'
    security_id: 'int'
    header_value: 'str'

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroupCtx:
    """ An instance of this class is attached to each channel using security groups.
    """

    channel_id: 'int'
    security_groups: 'intset'

    basic_auth_credentials: 'strdict'
    apikey_credentials: 'strdict'

    def __init__(self) -> 'None':

        # IDs of all the security groups attached to this channel
        security_groups:'intset' = set()

        # Maps usernames to _BasicAuthSecDef objects
        self.basic_auth_credentials = {}

        # Maps header values to _APIKeySecDef objects
        self.apikey_credentials = {}

        self._lock = RLock()

# ################################################################################################################################

    def check_security_basic_auth(self, username:'str', password:'str') -> 'bool':
        pass

# ################################################################################################################################

    def edit_basic_auth(self, security_id:'int') -> 'None':
        with self._lock:
            pass

# ################################################################################################################################

    def delete_basic_auth(self, security_id:'int') -> 'None':
        with self._lock:
            pass

# ################################################################################################################################

    def check_security_apikey(self, header:'str', value:'str') -> 'bool':
        pass

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

            # .. first, extract all the members from this group ..
            members = self._get_members_by_group_id(group_id)

            # .. now, go through each of the members found ..
            for member in members:

                # .. and add it to a container corresponding to its security type ..
                if member.sec_type == Sec_Def_Type.BASIC_AUTH:

                    # .. get the member's security definition ..
                    sec_def = self.server.worker_store.basic_auth_get_by_id(member.security_id)

                    # .. build a business object containing all the data needed in runtime ..
                    item = _BasicAuthSecDef()
                    item.group_id = group_id
                    item.member_id = member.id
                    item.security_id = sec_def['id']
                    item.password = sec_def['password']

                    # .. add the business object to the correct container ..
                    username:'str' = sec_def['username']
                    ctx.basic_auth_credentials[username] = item

                elif member.sec_type == Sec_Def_Type.APIKEY:

                    # .. get the member's security definition ..
                    sec_def = self.server.worker_store.apikey_get_by_id(member.security_id)

                    # .. build a business object containing all the data needed in runtime ..
                    item = _APIKeySecDef()
                    item.group_id = group_id
                    item.member_id = member.id
                    item.security_id = sec_def['id']
                    item.header_value = sec_def['password']

                    # .. add the business object to the correct container ..
                    ctx.apikey_credentials[item.header_value] = item

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

        ctx

# ################################################################################################################################
# ################################################################################################################################
