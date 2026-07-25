# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The disposition report layout of RFC 8098 and the disposition strings of RFC 4130
# section 7, with the MIC recomputed by hashlib over a literally typed entity.

# Zato
from zato.common.as2.inbound import handle
from zato.common.as2.outbound import build_message

# Zato
from .conformance_helpers import boundary_of, EDI_Entity, EDI_Payload, make_receiver_partnership, \
    make_sender_partnership, mic_over, Receiver_Identifier, split_multipart

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# RFC 4130 section 7.4.3 with RFC 8098 section 3.2.6 - the disposition field
# of a successfully processed message.
_disposition_processed = 'automatic-action/MDN-sent-automatically; processed'

# RFC 8098 section 3.1 - the report media type and its machine-readable part.
_report_content_type = 'multipart/report; report-type=disposition-notification'
_disposition_part_type = 'message/disposition-notification'

# ################################################################################################################################
# ################################################################################################################################

class TestMDNConformance:
    """ RFC 4130 section 7.4 with RFC 8098 - the receiver's MDN is a multipart/report
    whose machine-readable fields carry the literal disposition string and a MIC
    that recomputes with hashlib over the literally typed covered entity.
    """

    def test_report_layout_and_disposition_recompute(self, parties:'any_') -> 'None':
        sender_partnership = make_sender_partnership()
        sender_partnership.mdn_signed = False

        body, headers, message_id, sender_mic = build_message(sender_partnership, parties.sender, EDI_Payload)

        receiver_partnership = make_receiver_partnership()
        result = handle(body, headers, [receiver_partnership], parties.receiver)
        assert not result.is_error

        # The MDN is a multipart/report with the literal report type ..
        mdn_content_type = result.headers['Content-Type']
        assert mdn_content_type.startswith(_report_content_type)

        boundary = boundary_of(mdn_content_type)
        parts = split_multipart(result.body, boundary)

        # .. carrying the human-readable text part and the machine-readable one ..
        part_count = len(parts)
        assert part_count == 2

        machine_part = parts[1]
        machine_headers, _, machine_fields = machine_part.partition(b'\r\n\r\n')

        expected_part_header = f'Content-Type: {_disposition_part_type}'.encode('ascii')
        assert expected_part_header in machine_headers

        # .. whose fields carry the literal disposition string and the answered Message-ID ..
        fields = machine_fields.decode('ascii')

        assert f'Disposition: {_disposition_processed}' in fields
        assert f'Original-Message-ID: {message_id}' in fields
        assert f'Final-Recipient: rfc822; {Receiver_Identifier}' in fields

        # .. and a Received-Content-MIC that recomputes with hashlib alone
        # over the covered entity typed out byte by byte.
        expected_mic = mic_over(EDI_Entity)

        assert f'Received-Content-MIC: {expected_mic}' in fields
        assert sender_mic == expected_mic

# ################################################################################################################################
# ################################################################################################################################
