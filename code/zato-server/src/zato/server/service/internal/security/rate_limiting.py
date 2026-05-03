# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
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

    def handle(self):

        sec_def_id = int(self.request.input['id'])

        with closing(self.odb.session()) as session:

            item = session.query(SecurityBase).filter_by(id=sec_def_id).one()
            opaque = loads(item.opaque1) if item.opaque1 else {}
            rate_limiting = opaque.get('rate_limiting', [])

        self.response.payload = {'rate_limiting': rate_limiting}

# ################################################################################################################################
# ################################################################################################################################

class _RateLimitingSaveBase(AdminService):

    input = 'id', 'rules_json'

    def handle(self):

        input = self.request.input
        sec_def_id = int(input['id'])
        rules_json = input['rules_json']

        rule_dicts:'anylist' = loads(rules_json)

        for rule_dict in rule_dicts:
            SlottedCIDRRule.from_dict(rule_dict)

        with closing(self.odb.session()) as session:

            item = session.query(SecurityBase).filter_by(id=sec_def_id).one()
            opaque = loads(item.opaque1) if item.opaque1 else {}
            opaque['rate_limiting'] = rule_dicts
            item.opaque1 = dumps(opaque)
            session.add(item)
            session.commit()

# ################################################################################################################################
# ################################################################################################################################

class _RateLimitingClearCountersBase(AdminService):

    input = 'id', 'rule_index'

    def handle(self):
        pass

# ################################################################################################################################
# ################################################################################################################################

class BasicAuthRateLimitingGet(_RateLimitingGetBase):
    name = 'zato.security.basic-auth.rate-limiting.get'

# ################################################################################################################################

class BasicAuthRateLimitingSave(_RateLimitingSaveBase):
    name = 'zato.security.basic-auth.rate-limiting.save'

# ################################################################################################################################

class BasicAuthRateLimitingClearCounters(_RateLimitingClearCountersBase):
    name = 'zato.security.basic-auth.rate-limiting.clear-counters'

# ################################################################################################################################
# ################################################################################################################################

class APIKeyRateLimitingGet(_RateLimitingGetBase):
    name = 'zato.security.apikey.rate-limiting.get'

# ################################################################################################################################

class APIKeyRateLimitingSave(_RateLimitingSaveBase):
    name = 'zato.security.apikey.rate-limiting.save'

# ################################################################################################################################

class APIKeyRateLimitingClearCounters(_RateLimitingClearCountersBase):
    name = 'zato.security.apikey.rate-limiting.clear-counters'

# ################################################################################################################################
# ################################################################################################################################
