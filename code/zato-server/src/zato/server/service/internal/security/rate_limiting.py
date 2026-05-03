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
    from zato.common.typing_ import anylist

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

        # .. and return them.
        self.response.payload = {'rate_limiting': rate_limiting}

# ################################################################################################################################
# ################################################################################################################################

class _RateLimitingSaveBase(AdminService):

    input = 'id', 'rules_json'
    _broker_message_type = None

    def handle(self) -> 'None':

        # Extract input parameters ..
        input = self.request.input
        sec_def_id = int(input['id'])
        rules_json = input['rules_json']

        # .. parse and validate each rule ..
        rule_dicts:'anylist' = loads(rules_json)

        for item in rule_dicts:
            SlottedCIDRRule.from_dict(item)

        # .. persist to the ODB ..
        with closing(self.odb.session()) as session:

            row = session.query(SecurityBase).filter_by(id=sec_def_id).one()

            # .. parse the existing opaque column ..
            if row.opaque1:
                opaque = loads(row.opaque1)
            else:
                opaque = {}

            # .. set the rate limiting rules ..
            opaque['rate_limiting'] = rule_dicts
            row.opaque1 = dumps(opaque)
            session.add(row)
            session.commit()

        # .. and notify all workers via the config dispatcher.
        params = {
            'action': self._broker_message_type.value,
            'id': sec_def_id,
            'rule_dicts': rule_dicts,
        }
        self.config_dispatcher.publish(params)

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
