# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from imaplib import IMAP4
from smtplib import SMTPAuthenticationError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The words an IMAP login rejection speaks in - the protocol has no error codes,
# so the exception's text is what says the server refused the credentials.
_imap_auth_error_markers = ('auth', 'login')

# ################################################################################################################################
# ################################################################################################################################

def is_auth_error(e:'Exception') -> 'bool':
    """ Whether an exception speaks of rejected credentials - SMTP replies 535 and 534
    arrive as SMTPAuthenticationError, while IMAP rejections arrive as IMAP4.error
    whose text names the authentication. Alerting counts these separately, because
    their remedy is credentials, not networking.
    """
    if isinstance(e, SMTPAuthenticationError):
        return True

    if isinstance(e, IMAP4.error):
        text = str(e).lower()
        out = any(marker in text for marker in _imap_auth_error_markers)
        return out

    return False

# ################################################################################################################################

def join_addresses(value:'any_') -> 'str':
    """ Message recipients arrive as one address or as a list of them - either way,
    what goes to the audit log is one comma-joined string.
    """
    if isinstance(value, str):
        out = value
    elif value:
        out = ', '.join(value)
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class EMailAPI:
    def __init__(self, smtp:'any_', imap:'any_') -> 'None':
        self.smtp = smtp
        self.imap = imap

# ################################################################################################################################
# ################################################################################################################################

class BaseConnection:

    config: 'any_'
    config_no_sensitive: 'any_'

    def __repr__(self) -> 'str':
        return '<{} at {}, config:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

# ################################################################################################################################
# ################################################################################################################################
