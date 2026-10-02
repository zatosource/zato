# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.common.hl7.display import build_display_tree
from zato.common.json_internal import dumps
from zato.hl7v2 import parse_hl7
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ParseForDisplay(AdminService):
    """ Parses an HL7 payload and returns its display tree - the structured view
    the details overlay renders. Parsing happens here, server-side, over the generated
    model and its full field definitions - no HL7 parsing is reimplemented in the browser.
    """
    name = 'zato.hl7.parse-for-display'
    input = 'data'
    output = 'response_data'

    def handle(self) -> 'None':

        payload = self.request.input.data

        # A payload that does not parse comes back as a report too, never as a bare
        # exception, so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'tree': None,
            'error': '',
        }

        try:
            message = parse_hl7(payload, validate=False)
            report['tree'] = build_display_tree(message)
            report['is_ok'] = True

        except Exception:
            report['error'] = format_exc()

        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################
