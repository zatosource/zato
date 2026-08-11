# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.connection.email.common import EMailAPI as EMailAPI
from zato.server.connection.email.imap import GenericIMAPConnection as GenericIMAPConnection, IMAPAPI as IMAPAPI, \
    IMAPConnStore as IMAPConnStore, Microsoft365IMAPConnection as Microsoft365IMAPConnection, \
    _build_attachment_envelopes as _build_attachment_envelopes, _get_message_summary as _get_message_summary, \
    _insert_imap_audit_event as _insert_imap_audit_event
from zato.server.connection.email.smtp import Microsoft365SMTPConnection as Microsoft365SMTPConnection, SMTPAPI as SMTPAPI, \
    SMTPConnection as SMTPConnection, SMTPConnStore as SMTPConnStore

# ################################################################################################################################
# ################################################################################################################################
