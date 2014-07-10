# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from logging import getLogger, INFO
from traceback import format_exc

# Outbox
from outbox import AnonymousOutbox, Attachment, Email, Outbox

# Zato
from zato.common import Inactive, EMAIL
from zato.server.store import BaseAPI, BaseStore

logger = getLogger(__name__)

_modes = {
    EMAIL.SMTP.MODE.PLAIN.value: None,
    EMAIL.SMTP.MODE.SSL.value: 'SSL',
    EMAIL.SMTP.MODE.STARTTLS.value: 'TLS'
}

class EMailAPI(object):
    def __init__(self, smtp):
        self.smtp = smtp

class SMTPConnection(object):
    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive

        self.conn_args = [self.config.host.encode('utf-8'), int(self.config.port), self.config.mode_outbox,
            self.config.is_debug, self.config.timeout]

        if config.username or config.password:
            self.conn_class = Outbox
            self.conn_args.insert(0, self.config.username)
            self.conn_args.insert(0, self.config.password)
        else:
            self.conn_class = AnonymousOutbox

    def __repr__(self):
        return '<{} at {}, config:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    def send(self, msg):

        headers = msg.headers or {}
        atts = [Attachment(att['name'], StringIO(att['contents'])) for att in msg.attachments] if msg.attachments else []

        if 'From' not in msg.headers:
            headers['From'] = msg.from_

        body, html_body = (None, msg.body) if msg.is_html else (msg.body, None)
        email = Email(msg.to, msg.subject, body, html_body, msg.charset, headers, msg.is_rfc2231)

        try:
            with self.conn_class(*self.conn_args) as conn:
                conn.send(email, atts)
        except Exception, e:
            logger.warn('Could not send an SMTP message to `%s`, e:`%s`', self.config_no_sensitive, format_exc(e))
        else:
            if logger.isEnabledFor(INFO):
                atts_info = ', '.join(att.name for att in atts) if atts else None
                logger.info('SMTP message `%r` sent from `%r` to `%r`, attachments:`%r`',
                    msg.subject, msg.from_, msg.to, atts_info)

class SMTPAPI(BaseAPI):
    """ API to obtain SMTP connections through.
    """

class SMTPConnStore(BaseStore):
    """ Stores connections to SMTP.
    """
    def create_impl(self, config, config_no_sensitive):
        config.mode_outbox = _modes[config.mode]
        return SMTPConnection(config, config_no_sensitive)
