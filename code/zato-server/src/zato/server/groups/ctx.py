# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from uuid import uuid4

# gevent
from gevent.lock import RLock

# Zato
from zato.common.api import Groups, Sec_Def_Type
from zato.common.crypto.api import is_string_equal
from zato.common.groups import Member

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, boolnone, dict_, intanydict, intlist, intnone, intset, list_, strlist
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

class SecurityGroupsCtx:
    """ An instance of this class is attached to each channel using security groups.
    """
    # ID of a channel this ctx object is attached to
    channel_id: 'int'

    # IDs of all the security groups attached to this channel
    security_groups: 'intset'

    # Maps group IDs to security IDs
    group_to_sec_map: 'intanydict'

    # Maps usernames to _BasicAuthSecDef objects
    basic_auth_credentials: 'dict_[str, _BasicAuthSecDef]'

    # Maps header values to _APIKeySecDef objects
    apikey_credentials: 'dict_[str, _APIKeySecDef]'

    def __init__(self, server:'ParallelServer') -> 'None':

        self.server = server

        self.group_to_sec_map = {}
        self.security_groups = set()

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

    def _get_apikey_by_security_id(self, security_id:'int') -> '_APIKeySecDef | None':

        for value in self.apikey_credentials.values():
            if value.security_id == security_id:
                return value

# ################################################################################################################################

    def _has_security_id(self, security_id:'int') -> 'bool':
        """ Returns True if input security_id is among any groups that we handle. Returns False otherwise.
        """
        for sec_def_ids in self.group_to_sec_map.values():
            if security_id in sec_def_ids:
                return True

        # If we are here, it means that do not have that security ID
        return False

# ################################################################################################################################

    def _after_auth_created(
        self,
        group_id:'int',
        security_id:'int',
    ) -> 'None':

        # Store information that we are aware of this group ..
        self.security_groups.add(group_id)

        # .. map the group ID to a list of security definitions that are related to it, ..
        # .. note that a single group may point to multiple security IDs ..
        sec_def_id_list = self.group_to_sec_map.setdefault(group_id, set())
        sec_def_id_list.add(security_id)

# ################################################################################################################################

    def _after_auth_deleted(self, security_id:'int') -> 'None':

        for sec_def_ids in self.group_to_sec_map.values():
            if security_id in sec_def_ids:
                sec_def_ids.remove(security_id)

# ################################################################################################################################

    def _create_basic_auth(
        self,
        security_id:'int',
        username:'str',
        password:'str'
    ) -> 'None':

        # Build a business object containing all the data needed in runtime ..
        item = _BasicAuthSecDef()
        item.security_id = security_id
        item.username = username
        item.password = password

        # .. and add the business object to our container ..
        self.basic_auth_credentials[username] = item

# ################################################################################################################################

    def _create_apikey(
        self,
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

    def set_basic_auth(self, security_id:'int', username:'str', password:'str') -> 'None':

        if self._delete_basic_auth(security_id):
            self._create_basic_auth(security_id, username, password)

# ################################################################################################################################

    def edit_apikey(self, security_id:'int', header_value:'str') -> 'None':

        if self._delete_apikey(security_id):
            self._create_apikey(security_id, header_value)

# ################################################################################################################################

    def _delete_basic_auth(self, security_id:'int') -> 'boolnone':

        # Continue only if we recognize such a Basic Auth definition ..
        if sec_info := self._get_basic_auth_by_security_id(security_id):

            # .. delete the definition itself ..
            _ = self.basic_auth_credentials.pop(sec_info.username, None)

            # .. remove it from maps too ..
            self._after_auth_deleted(security_id)

            # .. and indicate to our caller that we are done.
            return True

# ################################################################################################################################

    def _delete_apikey(self, security_id:'int') -> 'boolnone':

        # Continue only if we recognize such an API key definition ..
        if sec_info := self._get_apikey_by_security_id(security_id):

            # .. delete the definition itself ..
            _ = self.apikey_credentials.pop(sec_info.header_value, None)

            # .. remove it from maps too ..
            self._after_auth_deleted(security_id)

            # .. and indicate to our caller that we are done.
            return True

# ################################################################################################################################

    def delete_basic_auth(self, security_id:'int') -> 'None':
        _ = self._delete_basic_auth(security_id)

# ################################################################################################################################

    def delete_apikey(self, security_id:'int') -> 'None':
        _ = self._delete_apikey(security_id)

# ################################################################################################################################

    def check_security_apikey(self, cid:'str', channel_name:'str', header_value:'str') -> 'intnone':

        if sec_info := self.apikey_credentials.get(header_value):
            return sec_info.security_id
        else:
            logger.info(f'Invalid API key; channel={channel_name}; cid={cid}')

# ################################################################################################################################

    def _on_basic_auth_created(
        self,
        group_id:'int',
        security_id:'int',
        username:'str',
        password:'str'
    ) -> 'None':

        # Create the base object ..
        self._create_basic_auth(security_id, username, password)

        # .. and populate common containers.
        self._after_auth_created(group_id, security_id)

# ################################################################################################################################

    def on_basic_auth_created(
        self,
        group_id:'int',
        security_id:'int',
        username:'str',
        password:'str'
    ) -> 'None':

        with self._lock:
            self._on_basic_auth_created(group_id, security_id, username, password)

# ################################################################################################################################

    def set_current_basic_auth(self, security_id:'int', current_username:'str', password:'str') -> 'None':
        with self._lock:
            self.set_basic_auth(security_id, current_username, password)

# ################################################################################################################################

    def _on_basic_auth_deleted(self, security_id:'int') -> 'None':
        self.delete_basic_auth(security_id)

# ################################################################################################################################

    def on_basic_auth_deleted(self, security_id:'int') -> 'None':
        with self._lock:
            self.delete_basic_auth(security_id)

# ################################################################################################################################

    def _on_apikey_created(
        self,
        group_id:'int',
        security_id:'int',
        header_value:'str',
    ) -> 'None':

        # Create the base object ..
        self._create_apikey(security_id, header_value)

        # .. and populate common containers.
        self._after_auth_created(group_id, security_id)

# ################################################################################################################################

    def on_apikey_created(
        self,
        group_id:'int',
        security_id:'int',
        header_value:'str',
    ) -> 'None':

        with self._lock:
            self._on_apikey_created(group_id, security_id, header_value)

# ################################################################################################################################

    def set_current_apikey(self, security_id:'int', header_value:'str') -> 'None':
        with self._lock:
            self.edit_apikey(security_id, header_value)

# ################################################################################################################################

    def _on_apikey_deleted(self, security_id:'int') -> 'None':
        _ = self._delete_apikey(security_id)

# ################################################################################################################################

    def on_apikey_deleted(self, security_id:'int') -> 'None':
        with self._lock:
            _ = self._delete_apikey(security_id)

# ################################################################################################################################

    def on_group_deleted(self, group_id:'int') -> 'None':

        # A list of all the Basic Auth usernames we are going to delete
        basic_auth_list:'strlist' = []

        # A list of all the API key header values we are going to delete
        apikey_list:'strlist' = []

        with self._lock:

            # Continue only if this group has been previously assigned to our context object ..
            if not group_id in self.security_groups:
                return

            # If we are here, it means that we really have a group to delete

            # Find all security IDs related to this group
            sec_id_list = self.group_to_sec_map.pop(group_id, [])

            # .. turn security IDs into their names (Basic Auth) ..
            for username, item in self.basic_auth_credentials.items():
                if item.security_id in sec_id_list:
                    basic_auth_list.append(username)

            # .. turn security IDs into their header values (API keys) ..
            for header_value, item in self.apikey_credentials.items():
                if item.security_id in sec_id_list:
                    apikey_list.append(header_value)

            # .. remove security definitions (Basic Auth) ..
            for item in basic_auth_list:
                _ = self.basic_auth_credentials.pop(item, None)

            # .. remove security definitions (API keys) ..
            for item in apikey_list:
                _ = self.apikey_credentials.pop(item, None)

            # .. and remove the group itself.
            try:
                _ = self.security_groups.remove(group_id)
            except KeyError:
                pass

# ################################################################################################################################

    def _get_sec_def_by_id(self, security_id:'int') -> 'anydict':

        # Let's try Basic Auth definitions first ..
        if not (sec_def := self.server.worker_store.basic_auth_get_by_id(security_id)):

            # .. if we do not have anything, it must be an API key definition then ..
            sec_def = self.server.worker_store.apikey_get_by_id(security_id)

        # If we do not have anything, we can only report an error
        if not sec_def:
            raise Exception(f'Security ID is neither Basic Auth nor API key -> {security_id}')

        # .. otherwise, we can return the definition to our caller.
        else:
            return sec_def

# ################################################################################################################################

    def _get_sec_def_type_by_id(self, security_id:'int') -> 'str':
        sec_def = self._get_sec_def_by_id(security_id)
        sec_def_type = sec_def['sec_type']
        return sec_def_type

# ################################################################################################################################

    def has_members(self) -> 'bool':
        return bool(self.basic_auth_credentials) or bool(self.apikey_credentials)

# ################################################################################################################################

    def on_member_added_to_group(self, group_id:'int', security_id:'int') -> 'None':

        with self._lock:

            # Continue only if this group has been previously assigned to our context object ..
            if not group_id in self.security_groups:
                return

            sec_def = self._get_sec_def_by_id(security_id)
            sec_def_type = sec_def['sec_type']

            # If we are here, we know we have everything to populate all the runtime containers
            if sec_def_type == Sec_Def_Type.BASIC_AUTH:
                self._on_basic_auth_created(group_id, security_id, sec_def['username'], sec_def['password'])
            else:
                self._on_apikey_created(group_id, security_id, sec_def['password'])

# ################################################################################################################################

    def _on_member_removed_from_group(self, group_id:'int', security_id:'int') -> 'None':

        # Continue only if this group has been previously assigned to our context object ..
        if not group_id in self.security_groups:
            return

        # First, remove the security ID from the input group ..
        self._after_auth_deleted(security_id)

        # .. now, check if the security definition belongs to other groups as well ..
        # .. and if not, delete the security definition altogether because ..
        # .. it must have been the last one group to have contained it ..
        for sec_def_ids in self.group_to_sec_map.values():
            if security_id in sec_def_ids:
                break
        else:
            # .. if we are here, it means that there was no break above ..
            # .. which means that the security ID is not in any group, ..
            # .. in which case we need to delete this definition now ..
            sec_def_type = self._get_sec_def_type_by_id(security_id)

            # .. do delete the definition from the correct container.
            if sec_def_type == Sec_Def_Type.BASIC_AUTH:
                self._on_basic_auth_deleted(security_id)
            else:
                self._on_apikey_deleted(security_id)

# ################################################################################################################################

    def on_member_removed_from_group(self, group_id:'int', security_id:'int') -> 'None':

        with self._lock:
            self._on_member_removed_from_group(group_id, security_id)

# ################################################################################################################################

    def on_group_assigned_to_channel(self, group_id:'int', members:'list_[Member]') -> 'None':

        # .. now, go through each of the members found ..
        for member in members:

            # .. and add it to a container corresponding to its security type ..
            if member.sec_type == Sec_Def_Type.BASIC_AUTH:

                # .. get the member's security definition ..
                sec_def = self.server.worker_store.basic_auth_get_by_id(member.security_id)

                # .. populate the correct container ..
                self.on_basic_auth_created(
                    group_id,
                    sec_def['id'],
                    sec_def['username'],
                    sec_def.get('password') or 'Zato-Not-Provided-Basic-Auth-' + uuid4().hex,
                )

            elif member.sec_type == Sec_Def_Type.APIKEY:

                # .. get the member's security definition ..
                sec_def = self.server.worker_store.apikey_get_by_id(member.security_id)

                # .. populate the correct container ..
                self.on_apikey_created(
                    group_id,
                    sec_def['id'],
                    sec_def.get('password') or 'Zato-Not-Provided-API-Key-' + uuid4().hex,
                )

# ################################################################################################################################

    def on_group_unassigned_from_channel(self, group_id:'int') -> 'None':

        with self._lock:

            # Pop the mapping which will also give us all the security definitions assigned to the group ..
            sec_id_list = self.group_to_sec_map.pop(group_id, [])

            # .. go through each definition ..
            for security_id in sec_id_list:

                # .. and remove it, if necessary.
                self._on_member_removed_from_group(group_id, security_id)

            # Lastly, delete the top-level container for groups.
            try:
                _ = self.security_groups.remove(group_id)
            except KeyError:
                pass

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroupsCtxBuilder:

    members: 'list_[Member]'

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

# ################################################################################################################################

    def populate_members(self) -> 'None':
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

    def build_ctx(self, channel_id:'int', security_groups: 'intlist') -> 'SecurityGroupsCtx':

        # Build a basic object ..
        ctx = SecurityGroupsCtx(self.server)

        # .. populate it with the core data ..
        ctx.channel_id = channel_id

        # .. add all the credentials ..
        for group_id in security_groups:

            # .. extract all the members from this group ..
            members = self._get_members_by_group_id(group_id)

            # .. add them to the channel ..
            ctx.on_group_assigned_to_channel(group_id, members)

        # .. and return the business object to our caller.
        return ctx

# ################################################################################################################################
# ################################################################################################################################
