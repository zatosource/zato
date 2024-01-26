# -# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from contextlib import contextmanager
from io import BytesIO
from logging import getLogger, INFO
from mimetypes import guess_type as guess_mime_type
from traceback import format_exc

# imbox
from zato.common.ext.imbox import Imbox as _Imbox
from zato.common.ext.imbox.imap import ImapTransport as _ImapTransport
from zato.common.ext.imbox.parser import parse_email, Struct

# Outbox
from zato.server.ext.outbox import AnonymousOutbox, Attachment, Email, Outbox

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring, unicode

# Zato
from zato.common.api import IMAPMessage, EMAIL
from zato.server.connection.cloud.microsoft_365 import Microsoft365Client
from zato.server.store import BaseAPI, BaseStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from O365.mailbox import MailBox
    from O365.message import Message as MS365Message
    from zato.common.typing_ import any_, anylist
    MailBox = MailBox
    MS365Message = MS365Message

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_modes = {
    EMAIL.SMTP.MODE.PLAIN: None,
    EMAIL.SMTP.MODE.SSL: 'SSL',
    EMAIL.SMTP.MODE.STARTTLS: 'TLS'
}

# ################################################################################################################################
# ################################################################################################################################

class GenericIMAPMessage(IMAPMessage):

    def delete(self):
        self.conn.delete(self.uid)

    def mark_seen(self):
        self.conn.mark_seen(self.uid)

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365IMAPMessage(IMAPMessage):
    impl: 'MS365Message'

    def delete(self):
        _ = self.impl.delete()

    def mark_seen(self):
        _ = self.impl.mark_as_read()

# ################################################################################################################################
# ################################################################################################################################

class Imbox(_Imbox):

    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive
        self.server = ImapTransport(self.config.host, self.config.port, self.config.mode==EMAIL.IMAP.MODE.SSL)
        self.connection = self.server.connect(self.config.username, self.config.password or '', self.config.debug_level)

    def __repr__(self):
        return '<{} at {}, config:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    def fetch_by_uid(self, uid):
        message, data = self.connection.uid('fetch', uid, '(BODY.PEEK[])')
        raw_email = data[0][1]

        if not isinstance(raw_email, unicode):
            raw_email = raw_email.decode('utf8')

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
# ################################################################################################################################

class ImapTransport(_ImapTransport):
    def connect(self, username, password, debug_level):
        self.server.debug = debug_level
        self.server.login(username, password)
        self.server.select()

        return self.server

# ################################################################################################################################
# ################################################################################################################################

class EMailAPI:
    def __init__(self, smtp, imap):
        self.smtp = smtp
        self.imap = imap

# ################################################################################################################################
# ################################################################################################################################

class _Connection:

    def __repr__(self):
        return '<{} at {}, config:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

# ################################################################################################################################
# ################################################################################################################################

class SMTPConnection(_Connection):
    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive

        self.conn_args = [
            self.config.host.encode('utf-8'),
            int(self.config.port),
            self.config.mode_outbox,
            self.config.is_debug,
            self.config.timeout
        ]

        if config.username or config.password:

            password = (self.config.password or '')
            username = (self.config.username or '')

            self.conn_class = Outbox

            self.conn_args.insert(0, password)
            self.conn_args.insert(0, username)

        else:
            self.conn_class = AnonymousOutbox

# ################################################################################################################################

    def send(self, msg, from_=None) -> 'bool':

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

            # Log what happened ..
            logger.warning('Could not send an SMTP message to `%s`, e:`%s`', self.config_no_sensitive, format_exc())

            # .. and tell the caller that the message was not sent.
            return False
        else:

            # Optionally, log what happened ..
            if logger.isEnabledFor(INFO):
                atts_info = ', '.join(att.name for att in atts) if atts else None
                logger.info('SMTP message `%r` sent from `%r` to `%r`, attachments:`%r`',
                    msg.subject, msg.from_, msg.to, atts_info)

            # .. and tell the caller that the message was sent successfully.
            return True

# ################################################################################################################################
# ################################################################################################################################

class SMTPAPI(BaseAPI):
    """ API to obtain SMTP connections through.
    """

# ################################################################################################################################
# ################################################################################################################################

class SMTPConnStore(BaseStore):
    """ Stores connections to SMTP.
    """
    def create_impl(self, config, config_no_sensitive):
        config.mode_outbox = _modes[config.mode]
        return SMTPConnection(config, config_no_sensitive)

# ################################################################################################################################
# ################################################################################################################################

class _IMAPConnection(_Connection):

    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive

    def get(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def ping(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def delete(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def mark_seen(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################

class GenericIMAPConnection(_IMAPConnection):

    @contextmanager
    def get_connection(self):
        conn = Imbox(self.config, self.config_no_sensitive)
        yield conn
        conn.close()
        conn.server.server.sock.close()

    def get(self, folder='INBOX'):
        with self.get_connection() as conn: # type: Imbox
            conn.connection.select(folder)

            for uid, msg in conn.fetch_list(' '.join(self.config.get_criteria.splitlines())):
                yield (uid, GenericIMAPMessage(uid, conn, msg))

    def ping(self):
        with self.get_connection() as conn: # type: Imbox
            conn.connection.noop()

    def delete(self, *uids):
        with self.get_connection() as conn: # type: Imbox
            for uid in uids:
                mov, data = self.connection.uid('STORE', uid, '+FLAGS', '(\\Deleted)')
            conn.connection.expunge()

    def mark_seen(self, *uids):
        with self.get_connection() as conn: # type: Imbox
            for uid in uids:
                conn.connection.uid('STORE', uid, '+FLAGS', '\\Seen')

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365IMAPConnection(_IMAPConnection):

    def _extract_list_of_addresses(self, native_elem:'any_') -> 'anylist':

        out = []
        elems = ((elem.name, elem.address) for elem in list(native_elem))

        # .. try to extract the recipients of the message ..
        for display_name, email in elems:
            out.append({
                'name': display_name,
                'email': email,
            })

        return out

# ################################################################################################################################

    def _extract_attachments(self, native_message:'MS365Message') -> 'anylist':

        # Our response to produce
        out = []

        attachments = list(native_message.attachments)
        for elem in attachments:

            mime_type, _ = guess_mime_type(elem.name)
            if not mime_type:
                mime_type = 'text/plain'

            content = elem.content
            if content:
                content = b64decode(content)
            else:
                content = b''

            size = len(content)
            content = BytesIO(content)

            out.append({
                'filename': elem.name,
                'size': size,
                'content': content,
                'content-type': mime_type
            })

        return out

# ################################################################################################################################

    def _convert_to_imap_message(self, msg_id:'str', native_message:'MS365Message') -> 'IMAPMessage':

        # A dict object to base the resulting message's struct on ..
        data_dict = {}

        # .. the message's body (always HTML)..
        body = {}
        body['plain'] = []
        body['html'] = [native_message.body]
        data_dict['body'] = body

        # .. who sent the message ..
        sent_from = {
            'name': native_message.sender.name,
            'email': native_message.sender.address
        }

        sent_to = self._extract_list_of_addresses(native_message.to)
        sent_cc = self._extract_list_of_addresses(native_message.cc)

        # .. populate the correspondents fields ..
        data_dict['sent_from'] = [sent_from]
        data_dict['sent_to'] = sent_to
        data_dict['cc'] = sent_cc

        # .. populate attachments ..
        attachments = self._extract_attachments(native_message)
        data_dict['attachments'] = attachments

        # .. build the remaining fields ..
        data_dict['message_id'] = msg_id
        data_dict['subject'] = native_message.subject

        # .. build the messages internal Struct object (as in generic IMAP connections) ..
        data = Struct(**data_dict)

        # .. now, construct the response ..
        out = Microsoft365IMAPMessage(msg_id, self, data)
        out.impl = native_message

        # .. and return it to our caller.
        return out

# ################################################################################################################################

    def _get_mailbox(self) -> 'MailBox':

        # Obtain a new connection ..
        client = Microsoft365Client(self.config)

        # .. get a handle to the user's underlying mailbox ..
        mailbox = client.impl.mailbox(resource=self.config['username'])

        # .. and return it to the caller.
        return mailbox

# ################################################################################################################################

    def get(self, folder='INBOX', filter=None):

        filter = filter or self.config['filter_criteria']

        # By default, we have nothing to return.
        default = []

        # Obtain a handle to a mailbox ..
        mailbox = self._get_mailbox()

        # .. try to look up a folder by its name ..
        folder = mailbox.get_folder(folder_name=folder)

        # .. if found, we can return all of its messages ..
        if folder:
            messages = folder.get_messages(limit=10_000, query=filter, download_attachments=True)
            for item in messages:
                msg_id = item.internet_message_id
                imap_message = self._convert_to_imap_message(msg_id, item)
                yield msg_id, imap_message

        else:
            for item in default:
                yield item

# ################################################################################################################################

    def ping(self):

        mailbox = self._get_mailbox()
        result = mailbox.get_folders()

        return result

# ################################################################################################################################
# ################################################################################################################################

class IMAPConnStore(BaseStore):
    """ Stores connections to IMAP.
    """

    _impl_class = {
        EMAIL.IMAP.ServerType.Generic: GenericIMAPConnection,
        EMAIL.IMAP.ServerType.Microsoft365: Microsoft365IMAPConnection,
    }

    def create_impl(self, config, config_no_sensitive):

        server_type = config.server_type or EMAIL.IMAP.ServerType.Generic
        class_ = self._impl_class[server_type]
        instance = class_(config, config_no_sensitive)

        return instance

# ################################################################################################################################
# ################################################################################################################################

class IMAPAPI(BaseAPI):
    """ API to obtain SMTP connections through.
    """

# ################################################################################################################################
# ################################################################################################################################
