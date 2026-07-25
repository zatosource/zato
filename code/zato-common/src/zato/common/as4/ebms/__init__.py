# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The ebMS 3.0 header of an AS4 message, spread over one module per concern.

- names - the namespace map and the fully qualified name of every element built or read
- build - the SOAP envelope and the eb:Messaging block of a user message, receipt, error or pull request
- parse - an eb:Messaging block that arrived, read into plain dataclasses
"""

# Zato
from zato.common.as4.ebms.build import build_envelope, build_error, build_pull_request, build_receipt, \
    build_user_message, new_message_id
from zato.common.as4.ebms.names import Body_Element_ID, Messaging_Element_ID
from zato.common.as4.ebms.parse import error_details_list, ErrorDetails, find_body, find_messaging, MessagingDetails, \
    parse_messaging, part_details_list, PartDetails, signal_details_list, SignalDetails, user_message_details_list, \
    UserMessageDetails

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'build_envelope',
    'build_error',
    'build_pull_request',
    'build_receipt',
    'build_user_message',
    'error_details_list',
    'find_body',
    'find_messaging',
    'new_message_id',
    'parse_messaging',
    'part_details_list',
    'signal_details_list',
    'user_message_details_list',
    'Body_Element_ID',
    'ErrorDetails',
    'MessagingDetails',
    'Messaging_Element_ID',
    'PartDetails',
    'SignalDetails',
    'UserMessageDetails',
)

# ################################################################################################################################
# ################################################################################################################################
