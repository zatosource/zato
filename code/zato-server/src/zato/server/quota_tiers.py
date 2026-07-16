# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import closing
from dataclasses import dataclass

# Zato
from zato.common.api import Groups, Quota_Tiers
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericObject as ModelGenericObject, SecurityBase
from zato.common.odb.query.generic import GenericObjectWrapper
from zato.common.typing_ import cast_
from zato.common.util.sql import get_dict_with_opaque

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intset, strdict, strdictlist, strdictnone, strlistdict
    from zato.server.base.parallel import ParallelServer

    # Dummy assignment to satisfy type checkers
    strdictnone = strdictnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.quota.tiers')

# ################################################################################################################################
# ################################################################################################################################

intruledict = dict[int, 'strdictlist']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TierResolution:
    """ The outcome of resolving quota tier assignments to concrete rules per security definition.
    """

    # Security definition id -> rule dicts coming from the tier that governs it
    rules_by_sec_def: 'intruledict'

    # Security definitions that carry their own literal rules - tiers never override these
    own_rules_sec_def_ids: 'intset'

# ################################################################################################################################
# ################################################################################################################################

class QuotaTiersManager:
    """ Manages quota tiers - named, reusable rate-limit rule sets stored in generic_object rows
    and referenced by security definitions and security groups.
    """

    def __init__(self, server:'ParallelServer', session:'any_' = None) -> 'None':
        self.server = server
        self.cluster_id = self.server.cluster_id

        # A session factory may be given explicitly, e.g. in tests - otherwise the server's one is used.
        if session:
            self.session = session
        else:
            self.session = self.server.odb.session

        # Security definitions whose rules were installed from a tier - used to clear
        # limits of definitions that are no longer governed by any tier.
        self._governed_sec_def_ids:'intset' = set()

# ################################################################################################################################

    def _row_to_tier(self, row:'strdict') -> 'strdict':
        """ Normalizes a generic_object row (with opaque keys merged in) to a tier dict.
        """
        out:'strdict' = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'rules': row['rules'],
        }

        return out

# ################################################################################################################################

    def create_tier(self, name:'str', description:'str', rules:'strdictlist') -> 'int':
        """ Creates a new tier and returns its id.
        """

        # Serialize the tier body to its opaque form ..
        tier_data = {'description': description, 'rules': rules}
        opaque = dumps(tier_data)

        # .. work in a new SQL transaction ..
        with closing(self.session()) as session:

            wrapper = GenericObjectWrapper(session, self.cluster_id)
            wrapper.type_ = Quota_Tiers.Type.Quota_Tier

            # .. do create the tier now ..
            insert = wrapper.create(name, opaque)
            session.execute(insert)
            session.commit()

            # .. and read it back to obtain its id.
            tier = wrapper.get(name)

        out = tier['id']
        return out

# ################################################################################################################################

    def edit_tier(self, tier_id:'int', name:'str', description:'str', rules:'strdictlist') -> 'None':
        """ Updates an existing tier, including a potential rename.
        """

        # Serialize the tier body to its opaque form ..
        tier_data = {'description': description, 'rules': rules}
        opaque = dumps(tier_data)

        # .. work in a new SQL transaction ..
        with closing(self.session()) as session:

            wrapper = GenericObjectWrapper(session, self.cluster_id)
            wrapper.type_ = Quota_Tiers.Type.Quota_Tier

            # .. build and run the update ..
            update = wrapper.update(name, opaque, id=tier_id)
            session.execute(update)
            session.commit()

# ################################################################################################################################

    def delete_tier(self, tier_id:'int') -> 'None':
        """ Deletes a tier by its id - reference checks belong to the calling service.
        """
        with closing(self.session()) as session:

            wrapper = GenericObjectWrapper(session, self.cluster_id)
            wrapper.type_ = Quota_Tiers.Type.Quota_Tier

            delete = wrapper.delete_by_id(tier_id)
            session.execute(delete)
            session.commit()

# ################################################################################################################################

    def get_tier(self, tier_id:'int') -> 'strdictnone':
        """ Returns a tier by its id or None if it does not exist.
        """
        with closing(self.session()) as session:

            row = session.query(ModelGenericObject).\
                filter(ModelGenericObject.id==tier_id).\
                filter(ModelGenericObject.type_==Quota_Tiers.Type.Quota_Tier).\
                filter(ModelGenericObject.cluster_id==self.cluster_id).\
                first()

            if row is None:
                return None

            row = cast_('strdict', get_dict_with_opaque(row))

        out = self._row_to_tier(row)
        return out

# ################################################################################################################################

    def get_tier_by_name(self, name:'str') -> 'strdictnone':
        """ Returns a tier by its name or None if it does not exist.
        """
        with closing(self.session()) as session:

            wrapper = GenericObjectWrapper(session, self.cluster_id)
            wrapper.type_ = Quota_Tiers.Type.Quota_Tier

            row = wrapper.get(name)

        if row is None:
            return None

        row = cast_('strdict', row)
        out = self._row_to_tier(row)
        return out

# ################################################################################################################################

    def get_tier_list(self) -> 'strdictlist':
        """ Returns all tiers, sorted by name.
        """

        # Our response to produce
        out:'strdictlist' = []

        with closing(self.session()) as session:

            wrapper = GenericObjectWrapper(session, self.cluster_id)
            wrapper.type_ = Quota_Tiers.Type.Quota_Tier

            rows = wrapper.get_list()

        for row in rows:
            tier = self._row_to_tier(row)
            out.append(tier)

        return out

# ################################################################################################################################

    def get_tier_referents(self, tier_id:'int') -> 'strlistdict':
        """ Returns the names of security definitions and groups that reference the given tier.
        """

        # Our response to produce
        out:'strlistdict' = {'security': [], 'groups': []}

        with closing(self.session()) as session:

            # Check security definitions first ..
            sec_rows = session.query(SecurityBase).\
                filter(SecurityBase.cluster_id==self.cluster_id).\
                all()

            for sec_row in sec_rows:

                # .. skip definitions without opaque data ..
                if not sec_row.opaque1:
                    continue

                opaque = loads(sec_row.opaque1)

                # .. and collect the ones pointing to our tier.
                if opaque.get('quota_tier') == tier_id:
                    out['security'].append(sec_row.name)

            # .. now check security groups.
            wrapper = GenericObjectWrapper(session, self.cluster_id)
            group_rows = wrapper.get_list(Groups.Type.Group_Parent, Groups.Type.API_Clients)

            for group_row in group_rows:
                if group_row.get('quota_tier') == tier_id:
                    out['groups'].append(group_row['name'])

        return out

# ################################################################################################################################

    def _extract_member_sec_def_id(self, member_name:'str') -> 'int':
        """ Extracts the security definition id from a member row name of the form '{sec_type}-{sec_def_id}-{group_id}'.
        """
        member_info = member_name.split('-')
        sec_def_id = member_info[1]

        out = int(sec_def_id)
        return out

# ################################################################################################################################

    def resolve_tier_assignments(self) -> 'TierResolution':
        """ Resolves all tier references to concrete rules per security definition.

        A definition's own literal rules always win, a tier set directly on a definition
        comes next, and a tier set on a group covers the remaining members of that group.
        """

        # Our response to produce
        out = TierResolution()
        out.rules_by_sec_def = {}
        out.own_rules_sec_def_ids = set()

        # Map each tier id to its rules for quick lookups below ..
        rules_by_tier:'intruledict' = {}
        tier_list = self.get_tier_list()

        for tier in tier_list:
            rules_by_tier[tier['id']] = tier['rules']

        with closing(self.session()) as session:

            # .. walk all security definitions to find own rules and direct tier references ..
            sec_rows = session.query(SecurityBase).\
                filter(SecurityBase.cluster_id==self.cluster_id).\
                all()

            for sec_row in sec_rows:

                # .. definitions without opaque data carry neither rules nor tiers ..
                if not sec_row.opaque1:
                    continue

                opaque = loads(sec_row.opaque1)

                # .. own literal rules always win ..
                if opaque.get('rate_limiting'):
                    out.own_rules_sec_def_ids.add(sec_row.id)
                    continue

                # .. otherwise a directly referenced tier applies.
                if tier_id := opaque.get('quota_tier'):
                    if rules := rules_by_tier.get(tier_id):
                        out.rules_by_sec_def[sec_row.id] = rules

            # .. now resolve group tiers for members that have neither own rules nor own tiers ..
            wrapper = GenericObjectWrapper(session, self.cluster_id)
            group_rows = wrapper.get_list(Groups.Type.Group_Parent, Groups.Type.API_Clients)

            for group_row in group_rows:

                # .. skip groups without a tier ..
                if not (group_tier_id := group_row.get('quota_tier')):
                    continue

                # .. skip groups pointing to a tier that no longer exists ..
                if not (group_rules := rules_by_tier.get(group_tier_id)):
                    continue

                group_id = group_row['id']
                member_rows = wrapper.get_list(
                    Groups.Type.Group_Member, Groups.Type.API_Clients, parent_object_id=group_id)

                for member_row in member_rows:
                    sec_def_id = self._extract_member_sec_def_id(member_row['name'])

                    # .. a definition's own rules take precedence over the group's tier ..
                    if sec_def_id in out.own_rules_sec_def_ids:
                        continue

                    # .. as does a tier set directly on the definition.
                    if sec_def_id in out.rules_by_sec_def:
                        continue

                    out.rules_by_sec_def[sec_def_id] = group_rules

        return out

# ################################################################################################################################

    def install_tier_assignments(self) -> 'None':
        """ Resolves all tier assignments and installs the resulting rules in the rate-limiting manager,
        clearing rules of definitions that are no longer governed by any tier.
        """
        resolution = self.resolve_tier_assignments()
        resolved_ids = set(resolution.rules_by_sec_def)

        # Definitions previously governed by a tier which no longer are, and which do not carry
        # their own rules either, must have their limits cleared.
        to_clear = self._governed_sec_def_ids - resolved_ids - resolution.own_rules_sec_def_ids

        for sec_def_id in to_clear:
            self.server.rate_limiting_manager.set_sec_def_config(sec_def_id, [])

        # Install the resolved rules - the rate-limiting manager receives plain rules
        # under each definition's id and cannot tell a tier was involved.
        for sec_def_id, rules in resolution.rules_by_sec_def.items():
            self.server.rate_limiting_manager.set_sec_def_config(sec_def_id, rules)

        # Remember what we installed for the next resolution pass.
        self._governed_sec_def_ids = resolved_ids

        installed_count = len(resolved_ids)
        cleared_count = len(to_clear)
        suffix = '' if installed_count == 1 else 's'

        logger.info('Quota tiers; installed rules for %d security definition%s, cleared %d',
            installed_count, suffix, cleared_count)

# ################################################################################################################################
# ################################################################################################################################
