# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import BAD_REQUEST, CONFLICT, FORBIDDEN, METHOD_NOT_ALLOWED, NOT_FOUND, OK, SERVICE_UNAVAILABLE

# Zato
from zato.common.json_internal import dumps, loads
from zato.common.rule_engine.ingestion import Outcome
from zato.common.rule_engine.invocation import InvocationStatus, is_ruleset_allowed, Message_Unknown_Ruleset, \
    parse_ruleset_path
from zato.common.rule_engine.sql.errors import DecisionBufferFullError
from zato.server.rule_engine_api import get_invoker
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.invocation import InvocationResult
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Content type of every response this API produces.
_content_type_json = 'application/json'

# The only method rulesets are invoked with.
_invoke_method = 'POST'

# Messages of this boundary's own errors - everything ruleset-specific comes from the invocation module.
_message_needs_authentication = 'This API requires authentication'
_message_needs_post           = 'Rulesets are invoked with POST'
_message_needs_json_object    = 'The request body has to be a JSON object'
_message_log_saturated        = 'The decision log cannot accept work right now, retry shortly'

# How each non-OK invocation status maps to an HTTP status code.
_status_code_map = {
    InvocationStatus.Unknown_Ruleset: NOT_FOUND,
    InvocationStatus.No_Live_Version: NOT_FOUND,
    InvocationStatus.Unknown_Version: NOT_FOUND,
    InvocationStatus.Ambiguous_Name:  CONFLICT,
    InvocationStatus.Invalid_Input:   BAD_REQUEST,
}

# ################################################################################################################################
# ################################################################################################################################

class RuleEngineAPIInvoke(AdminService):
    """ The one service behind every Rule engine API object.

    The channel it serves ends in `/{ruleset}`, so one URL space covers every published ruleset -
    `POST /api/rules/payments.discounts` runs the live version and appending `/versions/3` pins one.
    Which rulesets a caller may run is decided by the object's grants, and every evaluation lands
    in the decision log together with the calling system's name.
    """

    name = 'zato.rule-engine.api.invoke'

# ################################################################################################################################

    def _set_response(self, status_code:'int', body:'anydict') -> 'None':
        """ Sets one JSON response, no matter whether it reports a decision or an error.
        """
        self.response.status_code = status_code
        self.response.data_format = _content_type_json
        self.response.payload = dumps(body)

# ################################################################################################################################

    def _set_error(self, status_code:'int', ruleset:'str', message:'str') -> 'None':
        """ Sets one structured error response with a single readable message.
        """
        body = {
            'ruleset': ruleset,
            'errors': [{'message': message}],
        }
        self._set_response(status_code, body)

# ################################################################################################################################

    def _set_result(self, result:'InvocationResult') -> 'None':
        """ Turns one invocation result into its HTTP response.
        """
        # Anything but a completed evaluation is a structured error response ..
        if result.status != InvocationStatus.OK:
            status_code = _status_code_map[result.status]

            # .. input validation failures carry the validator's own domain-term errors ..
            if result.errors:
                body = {
                    'ruleset': result.ruleset,
                    'version': result.version,
                    'errors': result.errors,
                }
                self._set_response(status_code, body)

            # .. and everything else carries its one readable message.
            else:
                self._set_error(status_code, result.ruleset, result.message)

            return

        # .. a completed evaluation always carries the decision the log now holds.
        decision = result.decision
        assert decision is not None

        body = {
            'ruleset':     result.ruleset,
            'version':     result.version,
            'decision_id': decision['decision_id'],
            'outcome':     decision['outcome'],
            'outputs':     decision['actual'],
            'messages':    decision['fired'],
            'duration_ms': decision['duration_ms'],
        }

        # An input the rules could not evaluate is the caller's error - the decision
        # is in the log either way, under the same decision id the response carries.
        if decision['outcome'] == Outcome.Error:
            body['error'] = decision['error']
            self._set_response(BAD_REQUEST, body)
        else:
            self._set_response(OK, body)

# ################################################################################################################################

    def handle(self) -> 'None':
        """ Processes one ruleset invocation.
        """

        # The API requires authentication via security groups ..
        # .. if the HTTP layer did not authenticate the caller, reject immediately.
        channel_security = self.channel.security

        if not channel_security.id:
            logger.info(
                'Rule engine API `%s` rejected unauthenticated request (sec name=`%s` username=`%s`)',
                self.channel.name, channel_security.name, channel_security.username)
            self._set_error(FORBIDDEN, '', _message_needs_authentication)
            return

        # Look up this object's config - the entry may be gone if the object
        # is being deleted while this request is already in flight ..
        object_config = self.server.config_manager.gateway_rule_engine.get(self.channel.name)

        if object_config is None:
            logger.info(
                'Rule engine API `%s` has no config entry (object deleted) (sec name=`%s`)',
                self.channel.name, channel_security.name)
            self._set_error(NOT_FOUND, '', Message_Unknown_Ruleset.format(name=''))
            return

        # .. rulesets are only ever invoked with POST ..
        if self.request.http.method != _invoke_method:
            self._set_error(METHOD_NOT_ALLOWED, '', _message_needs_post)
            return

        # .. the one path parameter names the ruleset and optionally pins a version ..
        path_value = self.request.http.params['ruleset']
        parsed = parse_ruleset_path(path_value)

        if parsed.error:
            self._set_error(BAD_REQUEST, path_value, parsed.error)
            return

        # .. the object's grants decide which rulesets this API exposes at all - a name
        # outside the grants gets the same answer as a name that does not exist,
        # so credentials cannot be used to enumerate what exists ..
        granted_rulesets = object_config.get('rulesets') or []

        if not is_ruleset_allowed(parsed.name, granted_rulesets):
            logger.info(
                'Rule engine API `%s` refused ruleset `%s` (sec name=`%s`, grants=%s)',
                self.channel.name, parsed.name, channel_security.name, granted_rulesets)
            message = Message_Unknown_Ruleset.format(name=parsed.name)
            self._set_error(NOT_FOUND, parsed.name, message)
            return

        # .. the request body has to be one JSON object of vocabulary terms ..
        raw_request = self.request.raw

        if isinstance(raw_request, bytes):
            raw_request = raw_request.decode('utf8')

        # .. an empty body is an empty input, which the rules or the vocabulary judge themselves ..
        if raw_request:
            try:
                data = loads(raw_request)
            except ValueError:
                self._set_error(BAD_REQUEST, parsed.name, _message_needs_json_object)
                return
        else:
            data = {}

        if not isinstance(data, dict):
            self._set_error(BAD_REQUEST, parsed.name, _message_needs_json_object)
            return

        # .. run the ruleset, logging the decision under the calling system's name ..
        invoker = get_invoker()

        try:
            result = invoker.invoke(parsed.name, data, parsed.version, caller=channel_security.name)

        # .. a saturated decision log refuses work rather than dropping decisions silently.
        except DecisionBufferFullError:
            logger.warning(
                'Rule engine API `%s` refused ruleset `%s`, the decision buffer is full', self.channel.name, parsed.name)
            self._set_error(SERVICE_UNAVAILABLE, parsed.name, _message_log_saturated)
            return

        # .. and turn the outcome into the response.
        self._set_result(result)

# ################################################################################################################################
# ################################################################################################################################
