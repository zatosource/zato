# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import SECURITY
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import SecurityBase
from zato.common.rate_limiting.cidr import SlottedCIDRRule
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

class _RateLimitingGetBase(AdminService):

    input = 'id'

    def handle(self) -> 'None':

        # Read the security definition ID from the request ..
        input = self.request.input
        sec_def_id = int(input['id'])

        # .. look up the security definition in the ODB ..
        with closing(self.odb.session()) as session:

            item = session.query(SecurityBase).filter_by(id=sec_def_id).one()

            # .. parse the opaque column ..
            if item.opaque1:
                opaque = loads(item.opaque1)
            else:
                opaque = {}

            # .. extract rate limiting rules, which may not exist yet ..
            if 'rate_limiting' in opaque:
                rate_limiting = opaque['rate_limiting']
            else:
                rate_limiting = []

            # .. the same goes for a quota tier reference ..
            if 'quota_tier' in opaque:
                quota_tier = opaque['quota_tier']
            else:
                quota_tier = None

        # .. and return them.
        self.response.payload = {'rate_limiting': rate_limiting, 'quota_tier': quota_tier}

# ################################################################################################################################
# ################################################################################################################################

class _RateLimitingSaveBase(AdminService):

    input = 'id', '-rules_json', '-quota_tier'
    _broker_message_type:'any_' = None

    def _save_opaque(self, sec_def_id:'int', to_set:'str', value:'any_', to_remove:'str') -> 'None':
        """ Sets one opaque key and removes the other - a definition either references a tier or carries its own rules.
        """
        with closing(self.odb.session()) as session:

            row = session.query(SecurityBase).filter_by(id=sec_def_id).one()

            # .. parse the existing opaque column ..
            if row.opaque1:
                opaque = loads(row.opaque1)
            else:
                opaque = {}

            # .. set the new value and drop the mutually exclusive key ..
            opaque[to_set] = value
            _ = opaque.pop(to_remove, None)

            row.opaque1 = dumps(opaque)
            session.add(row)
            session.commit()

# ################################################################################################################################

    def handle(self) -> 'None':

        # Extract input parameters ..
        input = self.request.input
        sec_def_id = int(input['id'])
        rules_json = input.rules_json
        quota_tier = input.quota_tier

        self.logger.info('SecDefRateLimitingSave; sec_def_id:%s, rules_json:%s, quota_tier:%s',
            sec_def_id, rules_json, quota_tier)

        # .. a definition either references a tier or carries its own rules, never both ..
        if quota_tier:
            if rules_json:
                rule_dicts:'anylist' = loads(rules_json)
                if rule_dicts:
                    raise Exception('A security definition cannot have both a quota tier and its own rate limiting rules')

            # .. the tier must exist ..
            tier_id = int(quota_tier)
            if not self.server.quota_tiers_manager.get_tier(tier_id):
                raise Exception(f'Quota tier with id `{tier_id}` not found')

            # .. persist the reference ..
            self._save_opaque(sec_def_id, 'quota_tier', tier_id, 'rate_limiting')

            # .. and let all workers re-resolve tier assignments.
            params = {
                'action': SECURITY.QUOTA_TIER_EDIT.value,
                'id': tier_id,
            }
            self.config_dispatcher.publish(params)

            return

        # .. no tier on input, so this is the own-rules path ..
        if rules_json:
            rule_dicts = loads(rules_json)
        else:
            rule_dicts = []

        self.logger.info('SecDefRateLimitingSave; sec_def_id:%s, parsed %s rule_dicts:%s', sec_def_id, len(rule_dicts), rule_dicts)

        for item in rule_dicts:
            _ = SlottedCIDRRule.from_dict(item)

        # .. persist to the ODB ..
        self._save_opaque(sec_def_id, 'rate_limiting', rule_dicts, 'quota_tier')

        self.logger.info('SecDefRateLimitingSave; sec_def_id:%s, ODB committed', sec_def_id)

        # .. and notify all workers via the config dispatcher.
        params = {
            'action': self._broker_message_type.value,
            'id': sec_def_id,
            'rule_dicts': rule_dicts,
        }
        self.config_dispatcher.publish(params)

        self.logger.info('SecDefRateLimitingSave; sec_def_id:%s, config event published, action:%s', sec_def_id, self._broker_message_type.value)

# ################################################################################################################################
# ################################################################################################################################

class _RateLimitingClearCountersBase(AdminService):

    input = 'id', 'rule_index'
    _key_prefix_template = ''

    def handle(self) -> 'None':

        # Extract input parameters ..
        input = self.request.input
        sec_def_id = int(input['id'])
        rule_index = int(input['rule_index'])

        # .. build the key prefix for this security definition ..
        key_prefix = self._key_prefix_template.format(sec_def_id)

        # .. and clear the counters.
        self.server.rate_limiting_manager.clear_sec_def_rule_counters(sec_def_id, rule_index, key_prefix)

# ################################################################################################################################
# ################################################################################################################################

class BasicAuthRateLimitingGet(_RateLimitingGetBase):
    name = 'zato.security.basic-auth.rate-limiting.get'

# ################################################################################################################################

class BasicAuthRateLimitingSave(_RateLimitingSaveBase):
    name = 'zato.security.basic-auth.rate-limiting.save'
    _broker_message_type = SECURITY.BASIC_AUTH_RATE_LIMITING_EDIT

# ################################################################################################################################

class BasicAuthRateLimitingClearCounters(_RateLimitingClearCountersBase):
    name = 'zato.security.basic-auth.rate-limiting.clear-counters'
    _key_prefix_template = 'basic{}:'

# ################################################################################################################################
# ################################################################################################################################

class APIKeyRateLimitingGet(_RateLimitingGetBase):
    name = 'zato.security.apikey.rate-limiting.get'

# ################################################################################################################################

class APIKeyRateLimitingSave(_RateLimitingSaveBase):
    name = 'zato.security.apikey.rate-limiting.save'
    _broker_message_type = SECURITY.APIKEY_RATE_LIMITING_EDIT

# ################################################################################################################################

class APIKeyRateLimitingClearCounters(_RateLimitingClearCountersBase):
    name = 'zato.security.apikey.rate-limiting.clear-counters'
    _key_prefix_template = 'apikey{}:'

# ################################################################################################################################
# ################################################################################################################################
