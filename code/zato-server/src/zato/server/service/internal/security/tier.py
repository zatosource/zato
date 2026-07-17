# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.broker_message import SECURITY
from zato.common.json_internal import loads
from zato.common.rate_limiting.cidr import SlottedCIDRRule
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdictlist

# ################################################################################################################################
# ################################################################################################################################

def _parse_and_validate_rules(rules_json:'str') -> 'strdictlist':
    """ Parses the input JSON and validates each rule through the same path the rate-limiting engine uses.
    """
    rule_dicts:'strdictlist' = loads(rules_json)

    for item in rule_dicts:
        _ = SlottedCIDRRule.from_dict(item)

    return rule_dicts

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new quota tier.
    """
    name = 'zato.security.tier.create'
    input = 'name', '-description', 'rules_json'
    output = 'id', 'name'

    def handle(self) -> 'None':

        # Extract and validate the input ..
        input = self.request.input
        rule_dicts = _parse_and_validate_rules(input.rules_json)

        # .. refuse to create a duplicate ..
        if self.server.quota_tiers_manager.get_tier_by_name(input.name):
            raise Exception(f'A quota tier named `{input.name}` already exists')

        # .. create the tier now ..
        tier_id = self.server.quota_tiers_manager.create_tier(input.name, input.description, rule_dicts)

        # .. and return its details to our caller.
        self.response.payload.id = tier_id
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing quota tier and re-resolves all references to it.
    """
    name = 'zato.security.tier.edit'
    input = 'id', 'name', '-description', 'rules_json'
    output = 'id', 'name'

    def handle(self) -> 'None':

        # Extract and validate the input ..
        input = self.request.input
        tier_id = int(input.id)
        rule_dicts = _parse_and_validate_rules(input.rules_json)

        # .. the tier must exist ..
        if not self.server.quota_tiers_manager.get_tier(tier_id):
            raise Exception(f'Quota tier with id `{tier_id}` not found')

        # .. a rename must not clash with another tier ..
        if other := self.server.quota_tiers_manager.get_tier_by_name(input.name):
            if other['id'] != tier_id:
                raise Exception(f'A quota tier named `{input.name}` already exists')

        # .. save the changes ..
        self.server.quota_tiers_manager.edit_tier(tier_id, input.name, input.description, rule_dicts)

        # .. notify all workers so every definition referencing this tier is re-resolved ..
        params = {
            'action': SECURITY.QUOTA_TIER_EDIT.value,
            'id': tier_id,
        }
        self.config_dispatcher.publish(params)

        # .. and return the tier's details to our caller.
        self.response.payload.id = tier_id
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a quota tier, refusing if anything still references it.
    """
    name = 'zato.security.tier.delete'
    input = 'id'

    def handle(self) -> 'None':

        # Extract the input ..
        tier_id = int(self.request.input.id)

        # .. a referenced tier must not be deleted ..
        referents = self.server.quota_tiers_manager.get_tier_referents(tier_id)
        referent_names = referents['security'] + referents['groups'] + referents['channels']

        if referent_names:
            referent_names = sorted(referent_names)
            names = ', '.join(referent_names)
            raise Exception(f'Quota tier cannot be deleted, it is still referenced by: {names}')

        # .. no references, delete it now.
        self.server.quota_tiers_manager.delete_tier(tier_id)

# ################################################################################################################################
# ################################################################################################################################

class SetForGroup(AdminService):
    """ Sets or removes the quota tier reference of a security group.
    """
    name = 'zato.security.tier.set-for-group'
    input = 'group_id', '-quota_tier'

    def handle(self) -> 'None':

        # Extract the input ..
        input = self.request.input
        group_id = int(input.group_id)
        quota_tier = input.quota_tier

        # .. an empty tier on input means the reference is to be removed ..
        if quota_tier:
            tier_id = int(quota_tier)

            # .. the tier must exist ..
            if not self.server.quota_tiers_manager.get_tier(tier_id):
                raise Exception(f'Quota tier with id `{tier_id}` not found')
        else:
            tier_id = None

        # .. persist the reference ..
        self.server.groups_manager.set_group_quota_tier(group_id, tier_id)

        # .. and let all workers re-resolve tier assignments.
        params = {
            'action': SECURITY.QUOTA_TIER_EDIT.value,
            'id': group_id,
        }
        self.config_dispatcher.publish(params)

# ################################################################################################################################
# ################################################################################################################################

class Get(AdminService):
    """ Returns details of a single quota tier.
    """
    name = 'zato.security.tier.get'
    input = 'id'

    def handle(self) -> 'None':

        # Extract the input ..
        tier_id = int(self.request.input.id)

        # .. look the tier up ..
        tier = self.server.quota_tiers_manager.get_tier(tier_id)

        if not tier:
            raise Exception(f'Quota tier with id `{tier_id}` not found')

        # .. and return it to our caller.
        self.response.payload = tier

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns all quota tiers along with how many objects reference each one.
    """
    name = 'zato.security.tier.get-list'

    def handle(self) -> 'None':

        # Read all the tiers ..
        tier_list = self.server.quota_tiers_manager.get_tier_list()

        # .. attach the referent count to each one ..
        for tier in tier_list:
            tier_id = tier['id']
            referents = self.server.quota_tiers_manager.get_tier_referents(tier_id)
            security_count = len(referents['security'])
            group_count = len(referents['groups'])
            channel_count = len(referents['channels'])
            tier['referent_count'] = security_count + group_count + channel_count

        # .. and return the list to our caller.
        self.response.payload = tier_list

# ################################################################################################################################
# ################################################################################################################################
