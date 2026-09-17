# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import CHANNEL, SECURITY
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import HTTPSOAP
from zato.common.rate_limiting.cidr import SlottedCIDRRule
from zato.server.connection.http_soap.response_cache import get_default_config as get_default_response_cache_config, \
    parse_config as parse_response_cache_config, purge_channel as purge_response_cache
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingSave(AdminService):

    name = 'zato.http-soap.rate-limiting.save'
    input = 'id', '-rules_json', '-quota_tier'

    def _save_opaque(self, channel_id:'int', to_set:'str', value:'any_', to_remove:'str') -> 'None':
        """ Sets one opaque key and removes the other - a channel either references a tier or carries its own rules.
        """
        with closing(self.odb.session()) as session:

            row = session.query(HTTPSOAP).filter_by(id=channel_id).one()

            # .. parse the existing opaque1 or start with an empty dict ..
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

    def handle(self) -> 'None':

        input = self.request.input
        channel_id = int(input['id'])
        rules_json = input.rules_json
        quota_tier = input.quota_tier

        self.logger.info('RateLimitingSave; channel_id:%s, rules_json:%s, quota_tier:%s', channel_id, rules_json, quota_tier)

        # A channel either references a tier or carries its own rules, never both ..
        if quota_tier:
            if rules_json:
                rule_dicts:'anylist' = loads(rules_json)
                if rule_dicts:
                    raise Exception('A channel cannot have both a quota tier and its own rate limiting rules')

            # .. the tier must exist ..
            tier_id = int(quota_tier)
            if not self.server.quota_tiers_manager.get_tier(tier_id):
                raise Exception(f'Quota tier with id `{tier_id}` not found')

            # .. persist the reference ..
            self._save_opaque(channel_id, 'quota_tier', tier_id, 'rate_limiting')

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

        self.logger.info('RateLimitingSave; channel_id:%s, parsed %s rule_dicts:%s', channel_id, len(rule_dicts), rule_dicts)

        # .. validate each rule by running it through from_dict ..
        for item in rule_dicts:
            SlottedCIDRRule.from_dict(item)

        # .. persist to the ODB ..
        self._save_opaque(channel_id, 'rate_limiting', rule_dicts, 'quota_tier')

        self.logger.info('RateLimitingSave; channel_id:%s, ODB committed', channel_id)

        # After ODB commit, notify the config dispatcher so the in-process manager picks up the change
        params = {
            'action': CHANNEL.HTTP_SOAP_RATE_LIMITING_EDIT.value,
            'id': channel_id,
            'rule_dicts': rule_dicts,
        }
        self.config_dispatcher.publish(params)

        self.logger.info('RateLimitingSave; channel_id:%s, config event published', channel_id)

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingGet(AdminService):

    name = 'zato.http-soap.rate-limiting.get'
    input = 'id'

    def handle(self):

        channel_id = int(self.request.input['id'])

        with closing(self.odb.session()) as session:

            # Read the current row ..
            item = session.query(HTTPSOAP).filter_by(id=channel_id).one()

            # .. parse existing opaque1 ..
            opaque = loads(item.opaque1) if item.opaque1 else {}

            # .. extract rate_limiting, defaulting to an empty list ..
            rate_limiting = opaque.get('rate_limiting', [])

            # .. the same goes for a quota tier reference ..
            quota_tier = opaque.get('quota_tier')

        self.response.payload = {'rate_limiting': rate_limiting, 'quota_tier': quota_tier}

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingClearCounters(AdminService):

    name = 'zato.http-soap.rate-limiting.clear-counters'
    input = 'id', 'rule_index'

    def handle(self):

        channel_id = int(self.request.input['id'])
        rule_index = int(self.request.input['rule_index'])
        key_prefix = f'rest{channel_id}:'

        self.server.rate_limiting_manager.clear_rule_counters(channel_id, rule_index, key_prefix)

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheGet(AdminService):
    """ Returns the response caching configuration of a REST or SOAP channel, merged with defaults.
    """
    name = 'zato.http-soap.response-cache.get'
    input = 'id'

    def handle(self) -> 'None':

        channel_id = int(self.request.input['id'])

        with closing(self.odb.session()) as session:

            # Read the current row ..
            item = session.query(HTTPSOAP).filter_by(id=channel_id).one()

            # .. parse the existing opaque1 or start with an empty dict ..
            if item.opaque1:
                opaque = loads(item.opaque1)
            else:
                opaque = {}

            # .. and overlay whatever is stored on top of the defaults.
            config = get_default_response_cache_config()

            if stored := opaque.get('response_cache'):
                config.update(stored)

        self.response.payload = {'response_cache': config}

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheSave(AdminService):
    """ Saves the response caching configuration of a REST or SOAP channel and broadcasts the change.
    """
    name = 'zato.http-soap.response-cache.save'
    input = 'id', 'config_json'

    def handle(self) -> 'None':

        input = self.request.input
        channel_id = int(input['id'])
        config_json = input['config_json']

        self.logger.info('ResponseCacheSave; channel_id:%s, config_json:%s', channel_id, config_json)

        # Parse the JSON string into a config dict ..
        config:'strdict' = loads(config_json)

        with closing(self.odb.session()) as session:

            # Read the current row ..
            row = session.query(HTTPSOAP).filter_by(id=channel_id).one()

            # .. validate the config by running it through the parser, with the channel's own transport ..
            _ = parse_response_cache_config(config, row.transport)

            # .. parse the existing opaque1 or start with an empty dict ..
            if row.opaque1:
                opaque = loads(row.opaque1)
            else:
                opaque = {}

            # .. set the response_cache key ..
            opaque['response_cache'] = config

            # .. write it back ..
            row.opaque1 = dumps(opaque)
            session.add(row)
            session.commit()

        self.logger.info('ResponseCacheSave; channel_id:%s, ODB committed', channel_id)

        # After ODB commit, notify the config dispatcher so the in-process channel data picks up the change
        params = {
            'action': CHANNEL.HTTP_SOAP_RESPONSE_CACHE_EDIT.value,
            'id': channel_id,
            'response_cache': config,
        }
        self.config_dispatcher.publish(params)

        self.logger.info('ResponseCacheSave; channel_id:%s, config event published', channel_id)

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheClear(AdminService):
    """ Deletes all the cached responses of a REST or SOAP channel.
    """
    name = 'zato.http-soap.response-cache.clear'
    input = 'id'

    def handle(self) -> 'None':

        channel_id = int(self.request.input['id'])
        purge_response_cache(self.cache, channel_id)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
