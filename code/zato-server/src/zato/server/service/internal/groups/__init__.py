# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import closing
from json import dumps, loads
from operator import itemgetter

# Zato
from zato.common.api import CONNECTION, GENERIC, Groups, SEC_DEF_TYPE
from zato.common.broker_message import Groups as Broker_Message_Groups, SECURITY
from zato.common.exception import BadRequest
from zato.common.odb.model import GenericConn as ModelGenericConn, GenericObject as ModelGenericObject, SecurityBase
from zato.common.odb.query.generic import GroupsWrapper
from zato.common.util.gateway import find_stranded_oauth_gateway
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service import AsIs, Service

logger_groups = logging.getLogger('zato.groups.service')

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

ModelGenericObjectTable:'any_' = ModelGenericObject.__table__

# The type a bearer token definition may be stored under in a member's name, in addition to its own
_bearer_token_alias = 'bearer_token'

# Each type a member may have, mapped to the type of the security definition it stands for
_member_type_to_sec_type = {
    SEC_DEF_TYPE.BASIC_AUTH: SEC_DEF_TYPE.BASIC_AUTH,
    SEC_DEF_TYPE.APIKEY: SEC_DEF_TYPE.APIKEY,
    SEC_DEF_TYPE.OAUTH: SEC_DEF_TYPE.OAUTH,
    _bearer_token_alias: SEC_DEF_TYPE.OAUTH,
}

# ################################################################################################################################
# ################################################################################################################################

def get_skip_gateway_name(input:'any_') -> 'strnone':
    """ Returns the name of the MCP gateway whose own save validates its OAuth settings,
    which a change to a group therefore does not check, or None.
    """
    out = input.skip_gateway_name

    # An optional input that was not given is empty
    if not out:
        out = None

    return out

# ################################################################################################################################

def validate_member_id_list(service:'Service', member_id_list:'any_') -> 'None':
    """ Raises BadRequest unless each member is a security type and the id of an existing definition
    of that type, joined with a dash.
    """
    with closing(service.odb.session()) as session:

        for member_id in member_id_list:

            if not isinstance(member_id, str):
                raise BadRequest(service.cid, f'Invalid security group member `{member_id}`')

            parts = member_id.split('-')

            if len(parts) != 2:
                raise BadRequest(service.cid, f'Invalid security group member `{member_id}`')

            member_type, security_id = parts

            if member_type not in _member_type_to_sec_type:
                raise BadRequest(service.cid, f'Invalid security group member `{member_id}`')

            if not security_id.isdigit():
                raise BadRequest(service.cid, f'Invalid security group member `{member_id}`')

            sec_def = session.query(SecurityBase.id).\
                filter(SecurityBase.id == int(security_id)).\
                filter(SecurityBase.sec_type == _member_type_to_sec_type[member_type]).\
                first()

            if not sec_def:
                raise BadRequest(service.cid, f'Invalid security group member `{member_id}`')

# ################################################################################################################################

def _get_stored_member_names(member_id:'str', group_id:'int') -> 'strlist':
    """ Returns each name the member may be stored under in the given group - a bearer token definition
    may be stored under its alias too.
    """
    member_type, security_id = member_id.split('-')

    if _member_type_to_sec_type[member_type] == SEC_DEF_TYPE.OAUTH:
        member_type_list = [SEC_DEF_TYPE.OAUTH, _bearer_token_alias]
    else:
        member_type_list = [member_type]

    out:'strlist' = []

    for item in member_type_list:
        out.append(f'{item}-{security_id}-{group_id}')

    return out

# ################################################################################################################################

def find_stranded_gateway(
    service:'Service',
    group_id:'int',
    to_add:'strlist',
    to_remove:'strlist',
    is_group_deleted:'bool',
    skip_gateway_name:'strnone',
) -> 'strnone':
    """ Applies a change to the members of a group in a transaction that is rolled back afterwards,
    and returns the name of the first MCP gateway with OAuth on that the change would leave with no
    bearer token definition able to verify its tokens, or None if there is no such gateway.
    """
    with closing(service.odb.session()) as session:

        try:

            wrapper = GroupsWrapper(session)

            # A deleted group has no members left ..
            if is_group_deleted:
                delete = wrapper.delete_by_parent_object_id(group_id)
                _ = session.execute(delete)

            # .. while otherwise, the members removed are taken out ..
            else:
                for member_id in to_remove:
                    for name in _get_stored_member_names(member_id, group_id):
                        delete = wrapper.delete_by_name(name, parent_object_id=group_id)
                        _ = session.execute(delete)

            # .. and the ones added are put in.
            if to_add:
                member_list = []

                for member_id in to_add:
                    member_list.append({
                        'name': f'{member_id}-{group_id}',
                        GENERIC.ATTR_NAME: '',
                    })

                insert = wrapper.create_many(
                    member_list,
                    Groups.Type.Group_Member,
                    Groups.Type.API_Clients,
                    parent_object_id=group_id
                )
                _ = session.execute(insert)

            session.flush()

            out = find_stranded_oauth_gateway(session, [group_id], skip_gateway_name)

        finally:
            session.rollback()

    return out

# ################################################################################################################################

def raise_if_gateway_stranded(service:'Service', group_id:'int', gateway_name:'strnone') -> 'None':
    """ Raises BadRequest naming the MCP gateway a change to the given group would strand, if there is one.
    """
    if gateway_name is None:
        return

    with closing(service.odb.session()) as session:
        group = session.query(ModelGenericObject.name).filter(ModelGenericObject.id == group_id).one()

    msg = f'Security group `{group.name}` holds the only bearer token definition that verifies tokens ' + \
        f'for MCP gateway `{gateway_name}`, which has OAuth on'

    raise BadRequest(service.cid, msg)

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    """ Returns all groups matching the input criteria.
    """
    input:'any_' = 'group_type', '-needs_members', '-needs_short_members'

    def handle(self):

        group_type = self.request.input.group_type
        needs_members = self.request.input.needs_members
        needs_short_members = self.request.input.needs_short_members

        group_list = self.server.groups_manager.get_group_list(group_type)
        member_count = self.invoke(GetMemberCount, group_type=group_type)

        for item in group_list:
            group_id = item['id']
            group_member_count = member_count[group_id]
            item['member_count'] = group_member_count

            if needs_members:
                members = self.invoke(GetMemberList, group_type=group_type, group_id=group_id)
                if needs_short_members:
                    new_members = []
                    for member in members:
                        new_members.append({
                            'name': member['name'],
                        })
                    members = new_members

                members.sort(key=itemgetter('name')) # type: ignore
                if members:
                    item['members'] = members

            if (group_member_count == 0) or (group_member_count > 1):
                suffix = 's'
            else:
                suffix = ''

            item['description'] = f'{group_member_count} member{suffix}'

        self.response.payload = group_list

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    """ Creates a new group.
    """
    input:'any_' = 'group_type', 'name', AsIs('-member_id_list')
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input
        member_id_list = input.get('member_id_list') or []

        logger_groups.info('Create.handle: group_type=%s, name=%s, member_id_list=%s', input.group_type, input.name, member_id_list)

        id = self.server.groups_manager.create_group(input.group_type, input.name)

        if member_id_list:
            self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Add,
                group_id=id,
                member_id_list=member_id_list,
            )

        self.response.payload.id = id
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    """ Updates an existing group.
    """
    input:'any_' = 'id', 'group_type', 'name', AsIs('-member_id_list'), '-skip_gateway_name'
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input
        member_id_list = input.get('member_id_list') or []
        skip_gateway_name = get_skip_gateway_name(input)
        group_id = int(input.id)

        logger_groups.info('Edit.handle: id=%s, group_type=%s, name=%s, member_id_list=%s',
            input.id, input.group_type, input.name, member_id_list)

        # All the new members of this group
        to_add:'strlist' = []

        # All the members that have to be removed from the group
        to_remove:'strlist' = []

        # Nothing is written unless each member is a definition that exists
        validate_member_id_list(self, member_id_list)

        # The diff is computed even when the input list is empty - an empty list means
        # the caller wants all the current members removed from the group.
        group_members = self.server.groups_manager.get_member_list(input.group_type, group_id)

        logger_groups.info('Edit.handle: group_members=%s', group_members)

        input_member_ids = set(member_id_list)
        group_member_ids = {f'{m.sec_type}-{m.security_id}' for m in group_members}

        logger_groups.info('Edit.handle: input_member_ids=%s, group_member_ids=%s',
            input_member_ids, group_member_ids)

        for member_id in group_member_ids:
            if member_id not in input_member_ids:
                to_remove.append(member_id)

        for member_id in input_member_ids:
            if member_id not in group_member_ids:
                to_add.append(member_id)

        logger_groups.info('Edit.handle: to_add=%s, to_remove=%s', to_add, to_remove)

        # A gateway with OAuth on keeps a bearer token definition that verifies its tokens
        if to_remove:
            gateway_name = find_stranded_gateway(self, group_id, to_add, to_remove, False, skip_gateway_name)
            raise_if_gateway_stranded(self, group_id, gateway_name)

        self.server.groups_manager.edit_group(group_id, input.group_type, input.name)

        if to_add:
            _ = self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Add,
                group_id=input.id,
                member_id_list=to_add,
            )

        if to_remove:
            _ = self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Remove,
                group_id=input.id,
                member_id_list=to_remove,
                skip_gateway_name=skip_gateway_name,
            )

        self.response.payload.id = self.request.input.id
        self.response.payload.name = self.request.input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    """ Deletes an existing group.
    """
    input:'any_' = 'id', '-skip_gateway_name'

    def handle(self):

        # Local variables
        input = self.request.input
        group_id = int(input.id)
        skip_gateway_name = get_skip_gateway_name(input)

        logger_groups.info('Delete.handle: group_id=%s', group_id)

        # Gateways imported before their groups were stored by id refer to the group by its name ..
        with closing(self.odb.session()) as session:
            group = session.query(ModelGenericObject.name).filter(ModelGenericObject.id == group_id).one()

        # .. a gateway with OAuth on keeps a bearer token definition that verifies its tokens ..
        gateway_name = find_stranded_gateway(self, group_id, [], [], True, skip_gateway_name)
        raise_if_gateway_stranded(self, group_id, gateway_name)

        # .. delete this group from the database ..
        self.server.groups_manager.delete_group(group_id)

        # .. make sure the database configuration of channels using it is also updated ..
        to_update = []
        data = self.invoke('zato.http-soap.get-list', connection=CONNECTION.CHANNEL, paginate=False, skip_response_elem=True)

        for item in data:
            if security_groups := item.get('security_groups'):
                if group_id in security_groups:
                    security_groups.remove(group_id)
                    item['security_groups'] = security_groups
                    to_update.append(item)

        for item in to_update: # type: ignore
            _= self.invoke('zato.http-soap.edit', item)

        # .. and so is the configuration of MCP gateways using it.
        self._remove_from_gateways(group_id, group.name, skip_gateway_name)

# ################################################################################################################################

    def _remove_from_gateways(self, group_id:'int', group_name:'str', skip_gateway_name:'strnone') -> 'None':
        """ Removes the deleted group from the security groups of each MCP gateway that uses it,
        by its id or by its name.
        """
        to_update:'any_' = []

        with closing(self.odb.session()) as session:

            gateway_list = session.query(ModelGenericConn).\
                filter(ModelGenericConn.type_ == GENERIC.CONNECTION.TYPE.GATEWAY_MCP).\
                all()

            for gateway in gateway_list:

                if gateway.name == skip_gateway_name:
                    continue

                opaque = parse_instance_opaque_attr(gateway)

                # A gateway saved before security groups existed uses none
                if (security_groups := opaque.get('security_groups')) is None:
                    continue

                if (group_id in security_groups) or (group_name in security_groups):
                    to_update.append(gateway.id)

        for gateway_id in to_update:

            response = self.invoke('zato.generic.connection.get-by-id', {'id': gateway_id})
            gateway_dict = loads(response)

            security_groups = []

            for item in gateway_dict['security_groups']:
                if item != group_id and item != group_name:
                    security_groups.append(item)

            gateway_dict['security_groups'] = security_groups

            _ = self.invoke('zato.generic.connection.edit', gateway_dict)

            logger_groups.info('Delete: removed group id=%s from MCP gateway `%s`', group_id, gateway_dict['name'])

# ################################################################################################################################
# ################################################################################################################################

class GetMemberList(Service):
    """ Returns current members of a group.
    """
    input:'any_' = 'group_type', 'group_id', '-should_serialize'

    def handle(self):

        # Local variables
        input = self.request.input

        member_list = self.server.groups_manager.get_member_list(input.group_type, input.group_id)
        member_list = [elem.to_dict() for elem in member_list]

        if input.should_serialize:
            member_list = dumps(member_list)

        self.response.payload = member_list

# ################################################################################################################################
# ################################################################################################################################

class GetMemberCount(Service):
    """ Returns information about how many members are in each group.
    """
    input:'any_' = 'group_type', '-should_serialize'

    def handle(self):

        # Local variables
        input = self.request.input

        member_count = self.server.groups_manager.get_member_count(input.group_type)
        if input.should_serialize:
            member_count = dumps(member_count)
        self.response.payload = member_count

# ################################################################################################################################
# ################################################################################################################################

class EditMemberList(Service):
    """ Adds members to or removes them from a group.
    """
    input:'any_' = 'group_action', 'group_id', AsIs('-member_id_list'), AsIs('-members'), '-skip_gateway_name'

    def _get_member_id_list_from_name_list(self, member_name_list:'any_') -> 'strlist':

        # Our response to produce
        out:'strlist' = []

        # Make sure this is actually a list
        member_name_list = member_name_list if isinstance(member_name_list, list) else [member_name_list] # type: ignore

        # Get a list of all the security definitions possible, out of which we will be building our IDs.
        security_list = self.invoke('zato.security.get-list', skip_response_elem=True)
        for item in member_name_list:
            if isinstance(item, dict):
                item_name:'str' = item['name']
            else:
                item_name = item
            for security in security_list:
                if item_name == security['name']:
                    sec_type = security['sec_type']
                    sec_def_id = security['id']
                    member_name = f'{sec_type}-{sec_def_id}'
                    out.append(member_name)

        return out

# ################################################################################################################################

    def handle(self):

        # Local variables
        input = self.request.input

        logger_groups.info('EditMemberList.handle: group_action=%s, group_id=%s, member_id_list=%s, members=%s',
            input.group_action, input.group_id, input.get('member_id_list'), input.get('members'))

        # We need to have member IDs in further steps so if we have names, they have to be turned into IDs here.
        if not (member_id_list := input.get('member_id_list')):
            member_id_list = self._get_member_id_list_from_name_list(input.members)

        logger_groups.info('EditMemberList.handle: resolved member_id_list=%s', member_id_list)

        if not member_id_list:
            logger_groups.info('EditMemberList.handle: empty member_id_list, returning early')
            return

        # Nothing is written unless each member is a definition that exists ..
        validate_member_id_list(self, member_id_list)

        if input.group_action == Groups.Membership_Action.Add:
            func = self.server.groups_manager.add_members_to_group
        else:
            func = self.server.groups_manager.remove_members_from_group

            # .. and a gateway with OAuth on keeps a bearer token definition that verifies its tokens.
            group_id = int(input.group_id)
            skip_gateway_name = get_skip_gateway_name(input)

            gateway_name = find_stranded_gateway(self, group_id, [], member_id_list, False, skip_gateway_name)
            raise_if_gateway_stranded(self, group_id, gateway_name)

        logger_groups.info('EditMemberList.handle: calling %s with group_id=%s, member_id_list=%s',
            func.__name__, input.group_id, member_id_list)

        func(input.group_id, member_id_list)

        # Notify the config manager so the in-RAM security groups of running channels are updated too,
        # otherwise the change would only take effect after a server restart.
        msg = {
            'action': Broker_Message_Groups.Edit_Member_List.value,
            'group_action': input.group_action,
            'group_id': int(input.group_id),
            'member_id_list': member_id_list,
        }
        self.config_dispatcher.publish(msg)

        # Quota tier resolution depends on group membership, so the server re-resolves tier assignments too.
        msg = {
            'action': SECURITY.QUOTA_TIER_EDIT.value,
            'id': int(input.group_id),
        }
        self.config_dispatcher.publish(msg)

# ################################################################################################################################
# ################################################################################################################################
