# -# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import contextmanager
from io import BytesIO
from logging import getLogger, INFO
from traceback import format_exc

# imbox
from imbox import Imbox as _Imbox
from imbox.imap import ImapTransport as _ImapTransport
from imbox.parser import parse_email

# Outbox
from outbox import AnonymousOutbox, Attachment, Email, Outbox

# Python 2/3 compatibility
from past.builtins import basestring, unicode

# Zato
from zato.common import IMAPMessage, EMAIL
from zato.server.store import BaseAPI, BaseStore

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

_modes = {
    EMAIL.SMTP.MODE.PLAIN.value: None,
    EMAIL.SMTP.MODE.SSL.value: 'SSL',
    EMAIL.SMTP.MODE.STARTTLS.value: 'TLS'
}

# ################################################################################################################################

class Imbox(_Imbox):

    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive
        self.server = ImapTransport(self.config.host, self.config.port, self.config.mode==EMAIL.IMAP.MODE.SSL.value)
        self.connection = self.server.connect(self.config.username, self.config.password, self.config.debug_level)

    def __repr__(self):
        return '<{} at {}, config:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    def fetch_by_uid(self, uid):
        message, data = self.connection.uid('fetch', uid, '(BODY.PEEK[])')
        raw_email = data[0][1]

        email_object = parse_email(raw_email)

        return email_object

    def search(self, criteria):
        message, data = self.connection.uid('search', None, criteria)
        return data[0].split()

    def fetch_list(self, criteria):
        uid_list = self.search(criteria)

        for uid in uid_list:
            yield (uid, self.fetch_by_uid(uid))

    def close(self):
        self.connection.close()

# ################################################################################################################################

class ImapTransport(_ImapTransport):
    def connect(self, username, password, debug_level):
        self.server = self.transport(self.hostname, self.port)
        self.server.debug = debug_level
        self.server.login(username, password)
        self.server.select()

        return self.server

# ################################################################################################################################

class EMailAPI(object):
    def __init__(self, smtp, imap):
        self.smtp = smtp
        self.imap = imap

# ################################################################################################################################

class _Connection(object):

    def __repr__(self):
        return '<{} at {}, config:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

# ################################################################################################################################

class SMTPConnection(_Connection):
    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive

        self.conn_args = [self.config.host.encode('utf-8'), int(self.config.port), self.config.mode_outbox,
            self.config.is_debug, self.config.timeout]

        if config.username or config.password:

            password = (self.config.password or '').encode('utf-8')
            username = (self.config.username or '').encode('utf-8')

            self.conn_class = Outbox

            self.conn_args.insert(0, password)
            self.conn_args.insert(0, username)

        else:
            self.conn_class = AnonymousOutbox

    def send(self, msg, from_=None):

        headers = msg.headers or {}
        atts = []
        if msg.attachments:
            for item in msg.attachments:
                contents  = item['contents']
                contents = contents.encode('utf8') if isinstance(contents, unicode) else contents
                att = Attachment(item['name'], BytesIO(contents))
                atts.append(att)

        if 'From' not in msg.headers:
            headers['From'] = msg.from_

        if msg.cc and 'CC' not in headers:
            headers['CC'] = ', '.join(msg.cc) if not isinstance(msg.cc, basestring) else msg.cc

        if msg.bcc and 'BCC' not in headers:
            headers['BCC'] = ', '.join(msg.bcc) if not isinstance(msg.bcc, basestring) else msg.bcc

        body, html_body = (None, msg.body) if msg.is_html else (msg.body, None)
        email = Email(msg.to, msg.subject, body, html_body, msg.charset, headers, msg.is_rfc2231)

        try:
            with self.conn_class(*self.conn_args) as conn:
                conn.send(email, atts, from_ or msg.from_)
        except Exception:
            logger.warn('Could not send an SMTP message to `%s`, e:`%s`', self.config_no_sensitive, format_exc())
        else:
            if logger.isEnabledFor(INFO):
                atts_info = ', '.join(att.name for att in atts) if atts else None
                logger.info('SMTP message `%r` sent from `%r` to `%r`, attachments:`%r`',
                    msg.subject, msg.from_, msg.to, atts_info)

# ################################################################################################################################

class SMTPAPI(BaseAPI):
    """ API to obtain SMTP connections through.
    """

# ################################################################################################################################

class SMTPConnStore(BaseStore):
    """ Stores connections to SMTP.
    """
    def create_impl(self, config, config_no_sensitive):
        config.mode_outbox = _modes[config.mode]
        return SMTPConnection(config, config_no_sensitive)

# ################################################################################################################################

class IMAPConnection(_Connection):
    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive

    @contextmanager
    def get_connection(self):
        conn = Imbox(self.config, self.config_no_sensitive)
        yield conn
        conn.close()

    def get(self, folder='INBOX'):
        with self.get_connection() as conn:
            conn.connection.select(folder)

            for uid, msg in conn.fetch_list(' '.join(self.config.get_criteria.splitlines())):
                yield (uid, IMAPMessage(uid, conn, msg))

    def ping(self):
        with self.get_connection() as conn:
            conn.connection.noop()

    def delete(self, *uids):
        with self.get_connection() as conn:
            for uid in uids:
                mov, data = self.connection.uid('STORE', uid, '+FLAGS', '(\\Deleted)')
            conn.connection.expunge()

    def mark_seen(self, *uids):
        with self.get_connection() as conn:
            for uid in uids:
                conn.connection.uid('STORE', uid, '+FLAGS', '\\Seen')

# ################################################################################################################################

class IMAPAPI(BaseAPI):
    """ API to obtain SMTP connections through.
    """

# ################################################################################################################################

class IMAPConnStore(BaseStore):
    """ Stores connections to IMAP.
    """
    def create_impl(self, config, config_no_sensitive):
        return IMAPConnection(config, config_no_sensitive)

# ################################################################################################################################
