# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from io import BytesIO
from json import dumps
from logging import getLogger, INFO
from mimetypes import guess_type as guess_mime_type
from time import monotonic
from traceback import format_exc

# Outbox
from zato.server.ext.outbox import AnonymousOutbox, Attachment, Email, Outbox

# Zato
from zato.common.api import EMAIL
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import build_attachment
from zato.common.util.api import new_cid_server
from zato.server.connection.cloud.microsoft_365 import Microsoft365Client
from zato.server.connection.email.common import is_auth_error, join_addresses, BaseConnection
from zato.server.store import BaseAPI, BaseStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from O365.mailbox import MailBox
    from zato.common.typing_ import any_, anylist, stranydict
    MailBox = MailBox

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

# What a Graph message calls its body's content type - HTML is the default
# for new messages, so only the plain-text kind is set explicitly.
_ms365_body_type_text = 'Text'

# Connections created before these fields existed have no such keys stored at all
_default_ca_certs_path    = ''
_default_helo_hostname    = ''
_default_from_address     = ''
_default_needs_tls_verify = True

# ################################################################################################################################
# ################################################################################################################################

def _get_send_summary(msg:'any_', from_:'any_') -> 'str':
    """ Builds a JSON summary of an outgoing e-mail message for the audit log.
    """

    # The body may be bytes, depending on how the caller built the message
    body = msg.body

    if isinstance(body, bytes):
        body = body.decode('utf-8', errors='replace')

    out = dumps({
        'subject': msg.subject,
        'from': from_ or msg.from_,
        'to': join_addresses(msg.to),
        'cc': join_addresses(msg.cc),
        'bcc': join_addresses(msg.bcc),
        'body': body,
    })

    return out

# ################################################################################################################################

def _insert_send_event(
    audit_log:'AuditLog',
    conn_name:'str',
    msg:'any_',
    from_:'any_',
    cid:'str',
    send_start:'float',
    attachment_envelopes:'anylist',
    *,
    outcome:'str',
    status:'str' = '',
    is_auth_error:'bool' = False,
    ) -> 'None':
    """ Writes one message-sent event describing a direct e-mail send, successful or not.
    A rejection of the credentials gets the auth-failed event type,
    because its remedy is different and alerting counts it separately.
    """
    duration_ms = int((monotonic() - send_start) * 1000)
    data = _get_send_summary(msg, from_)

    if is_auth_error:
        event_type = AuditEvent.Auth_Failed
    else:
        event_type = AuditEvent.Message_Sent

    audit_log.insert(
        AuditSource.Email_SMTP,
        event_type,
        conn_name,
        cid=cid,
        endpoint=join_addresses(msg.to),
        size=len(data),
        outcome=outcome,
        status=status,
        duration_ms=duration_ms,
        data=data,
        attachments=attachment_envelopes,
    )

# ################################################################################################################################

def _build_send_attachment_envelope(name:'str', contents:'bytes') -> 'any_':
    """ Builds one audit envelope describing an attachment as it goes out.
    """
    mime_type, _ = guess_mime_type(name)
    if not mime_type:
        mime_type = 'text/plain'

    out = build_attachment(name, mime_type, contents)
    return out

# ################################################################################################################################
# ################################################################################################################################

class SMTPConnection(BaseConnection):
    def __init__(self, config:'any_', config_no_sensitive:'any_', audit_log:'AuditLog') -> 'None':
        self.config = config
        self.config_no_sensitive = config_no_sensitive
        self.audit_log = audit_log

        # Each connection can have its audit log turned off individually - connections
        # created before the flag existed have no such key stored at all.
        if 'is_audit_log_active' in config:
            self.needs_audit = config['is_audit_log_active']
        else:
            self.needs_audit = True

        self.conn_args:'anylist' = [
            self.config.host.encode('utf-8'),
            int(self.config.port),
            self.config.mode_outbox,
            self.config.is_debug,
            self.config.timeout
        ]

        # Connections created before these fields existed have no such keys stored at all ..
        if 'ca_certs_path' in config:
            ca_certs_path = config['ca_certs_path']
        else:
            ca_certs_path = _default_ca_certs_path

        if 'helo_hostname' in config:
            helo_hostname = config['helo_hostname']
        else:
            helo_hostname = _default_helo_hostname

        if 'from_address' in config:
            from_address = config['from_address']
        else:
            from_address = _default_from_address

        if 'needs_tls_verify' in config:
            needs_tls_verify = config['needs_tls_verify']
        else:
            needs_tls_verify = _default_needs_tls_verify

        # .. and they may be empty strings in the configuration while the underlying transport expects None in such cases.
        if not ca_certs_path:
            ca_certs_path = None

        if not helo_hostname:
            helo_hostname = None

        if not from_address:
            from_address = None

        self.conn_kwargs:'stranydict' = {
            'needs_tls_verify': needs_tls_verify,
            'ca_certs_path': ca_certs_path,
            'helo_hostname': helo_hostname,
            'from_address': from_address,
        }

        if config.username or config.password:

            # Either credential may be None when only the other one was configured
            password = self.config.password
            if password is None:
                password = ''

            username = self.config.username
            if username is None:
                username = ''

            self.conn_class = Outbox

            self.conn_args.insert(0, password)
            self.conn_args.insert(0, username)

        else:
            self.conn_class = AnonymousOutbox

# ################################################################################################################################

    def ping(self) -> 'str':
        """ Connects to the server, authenticating as configured, without sending any message.
        Returns the server's EHLO response.
        """
        cid = new_cid_server()
        start = monotonic()

        # The transport opens and closes its own connection during a ping
        conn = self.conn_class(*self.conn_args, **self.conn_kwargs)

        # A failed ping is recorded too, before the caller learns about it
        try:
            out = conn.ping()
        except Exception as e:
            if self.needs_audit:
                self._insert_ping_event(cid, start, outcome=AuditOutcome.Error, status=str(e),
                    is_auth_error=is_auth_error(e))
            raise

        # A ping is traffic like any other to the audit log
        if self.needs_audit:
            self._insert_ping_event(cid, start, outcome=AuditOutcome.OK)

        return out

# ################################################################################################################################

    def _insert_ping_event(
        self,
        cid:'str',
        start:'float',
        *,
        outcome:'str',
        status:'str' = '',
        is_auth_error:'bool' = False,
        ) -> 'None':
        """ Writes one request-sent event describing a ping of this connection.
        A rejection of the credentials gets the auth-failed event type,
        because its remedy is different and alerting counts it separately.
        """
        duration_ms = int((monotonic() - start) * 1000)

        if is_auth_error:
            event_type = AuditEvent.Auth_Failed
        else:
            event_type = AuditEvent.Request_Sent

        self.audit_log.insert(
            AuditSource.Email_SMTP,
            event_type,
            self.config.name,
            cid=cid,
            endpoint=f'{self.config.host}:{self.config.port}',
            outcome=outcome,
            status=status,
            duration_ms=duration_ms,
        )

# ################################################################################################################################

    def send(self, msg:'any_', from_:'any_'=None, cid:'str'='') -> 'bool':

        # A message built without headers carries None there
        headers = msg.headers
        if headers is None:
            headers = {}
        atts = []
        attachment_envelopes:'anylist' = []

        if msg.attachments:
            for item in msg.attachments:
                contents  = item['contents']
                contents = contents.encode('utf8') if isinstance(contents, str) else contents
                att = Attachment(item['name'], BytesIO(contents))
                atts.append(att)

                # The audit log keeps the attachment's bytes as they went out
                if self.needs_audit:
                    attachment_envelopes.append(_build_send_attachment_envelope(item['name'], contents))

        # Messages without an explicit From address use the connection's own one, filled in by the underlying transport
        if 'From' not in msg.headers:
            if msg.from_:
                headers['From'] = msg.from_

        if msg.cc and 'CC' not in headers:
            headers['CC'] = ', '.join(msg.cc) if not isinstance(msg.cc, str) else msg.cc

        if msg.bcc and 'BCC' not in headers:
            headers['BCC'] = ', '.join(msg.bcc) if not isinstance(msg.bcc, str) else msg.bcc

        body, html_body = (None, msg.body) if msg.is_html else (msg.body, None)
        email = Email(msg.to, msg.subject, body, html_body, msg.charset, headers, msg.is_rfc2231)

        send_start = monotonic()

        try:
            with self.conn_class(*self.conn_args, **self.conn_kwargs) as conn:
                conn.send(email, atts, from_ or msg.from_)
        except Exception as e:

            # Log what happened ..
            logger.warning('Could not send an SMTP message to `%s`, e:`%s`', self.config_no_sensitive, format_exc())

            # .. record the failure before telling the caller ..
            if self.needs_audit:
                _insert_send_event(self.audit_log, self.config.name, msg, from_, cid, send_start, attachment_envelopes,
                    outcome=AuditOutcome.Error, status=str(e), is_auth_error=is_auth_error(e))

            # .. and tell the caller that the message was not sent.
            return False
        else:

            # Optionally, log what happened ..
            if logger.isEnabledFor(INFO):
                atts_info = ', '.join(att.name for att in atts) if atts else None
                logger.info('SMTP message `%r` sent from `%r` to `%r`, attachments:`%r`',
                    msg.subject, msg.from_, msg.to, atts_info)

            # .. record what went out on the wire ..
            if self.needs_audit:
                _insert_send_event(self.audit_log, self.config.name, msg, from_, cid, send_start, attachment_envelopes,
                    outcome=AuditOutcome.OK)

            # .. and tell the caller that the message was sent successfully.
            return True

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365SMTPConnection(BaseConnection):
    """ Sends e-mail through the Graph mailbox of a Microsoft 365 account,
    serving the same interface the generic SMTP connection serves.
    """
    def __init__(self, config:'any_', config_no_sensitive:'any_', audit_log:'AuditLog') -> 'None':
        self.config = config
        self.config_no_sensitive = config_no_sensitive
        self.audit_log = audit_log

        # Each connection can have its audit log turned off individually - connections
        # created before the flag existed have no such key stored at all.
        if 'is_audit_log_active' in config:
            self.needs_audit = config['is_audit_log_active']
        else:
            self.needs_audit = True

# ################################################################################################################################

    def _get_mailbox(self) -> 'MailBox':

        # Obtain a new client ..
        client = Microsoft365Client(self.config)

        # .. get a handle to the user's underlying mailbox - the lookup goes through
        # .. the client itself, which is what builds the account on first use ..
        mailbox = client.mailbox(resource=self.config['username'])

        # .. and return it to the caller.
        return mailbox

# ################################################################################################################################

    def ping(self) -> 'str':
        """ Confirms the mailbox is reachable through the Graph API, without sending any message.
        """
        cid = new_cid_server()
        start = monotonic()

        # A failed ping is recorded too, before the caller learns about it
        try:
            mailbox = self._get_mailbox()
            _ = mailbox.get_folders(limit=1)
        except Exception as e:
            if self.needs_audit:
                self._insert_ping_event(cid, start, outcome=AuditOutcome.Error, status=str(e))
            raise

        # A ping is traffic like any other to the audit log
        if self.needs_audit:
            self._insert_ping_event(cid, start, outcome=AuditOutcome.OK)

        out = f'Mailbox `{self.config["username"]}` is reachable'
        return out

# ################################################################################################################################

    def _insert_ping_event(
        self,
        cid:'str',
        start:'float',
        *,
        outcome:'str',
        status:'str' = '',
        ) -> 'None':
        """ Writes one request-sent event describing a ping of this connection.
        """
        duration_ms = int((monotonic() - start) * 1000)

        self.audit_log.insert(
            AuditSource.Email_SMTP,
            AuditEvent.Request_Sent,
            self.config['name'],
            cid=cid,
            endpoint=self.config['username'],
            outcome=outcome,
            status=status,
            duration_ms=duration_ms,
        )

# ################################################################################################################################

    def send(self, msg:'any_', from_:'any_'=None, cid:'str'='') -> 'bool':

        attachment_envelopes:'anylist' = []
        send_start = monotonic()

        try:

            # Obtain a handle to the mailbox the message goes out through ..
            mailbox = self._get_mailbox()
            message = mailbox.new_message()

            # .. fill in the recipients - each kind may be one address or a list of them ..
            message.to.add(msg.to)

            if msg.cc:
                message.cc.add(msg.cc)

            if msg.bcc:
                message.bcc.add(msg.bcc)

            # .. the subject goes in as it is ..
            message.subject = msg.subject

            # .. the body may be bytes, depending on how the caller built the message ..
            body = msg.body

            if isinstance(body, bytes):
                body = body.decode('utf-8', errors='replace')

            # .. Graph messages default to HTML, so only a plain-text one says so explicitly ..
            if not msg.is_html:
                message.body_type = _ms365_body_type_text

            message.body = body

            # .. attachments travel inside the message itself ..
            if msg.attachments:
                for item in msg.attachments:
                    contents = item['contents']
                    contents = contents.encode('utf8') if isinstance(contents, str) else contents
                    message.attachments.add([(BytesIO(contents), item['name'])])

                    # The audit log keeps the attachment's bytes as they went out
                    if self.needs_audit:
                        attachment_envelopes.append(_build_send_attachment_envelope(item['name'], contents))

            # .. and now the message can be sent ..
            is_sent = message.send()

            # .. an account configured not to raise reports a refusal as a plain False.
            if not is_sent:
                raise Exception(f'Message could not be sent through `{self.config["name"]}`')

        except Exception as e:

            # Log what happened ..
            logger.warning('Could not send a Microsoft 365 message to `%s`, e:`%s`', self.config_no_sensitive, format_exc())

            # .. record the failure before telling the caller ..
            if self.needs_audit:
                _insert_send_event(self.audit_log, self.config['name'], msg, from_, cid, send_start, attachment_envelopes,
                    outcome=AuditOutcome.Error, status=str(e))

            # .. and tell the caller that the message was not sent.
            return False
        else:

            # Optionally, log what happened ..
            if logger.isEnabledFor(INFO):
                logger.info('Microsoft 365 message `%r` sent to `%r` through `%r`',
                    msg.subject, msg.to, self.config['name'])

            # .. record what went out on the wire ..
            if self.needs_audit:
                _insert_send_event(self.audit_log, self.config['name'], msg, from_, cid, send_start, attachment_envelopes,
                    outcome=AuditOutcome.OK)

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

    _impl_class = {
        EMAIL.SMTP.ServerType.Generic: SMTPConnection,
        EMAIL.SMTP.ServerType.Microsoft365: Microsoft365SMTPConnection,
    }

    def __init__(self, server_name:'str') -> 'None':
        super().__init__()

        # All SMTP connections write their audit events through this object
        self.audit_log = AuditLog(server_name)

    def create_impl(self, config:'any_', config_no_sensitive:'any_') -> 'BaseConnection':

        # Connections created before the server type existed have no such key stored at all
        if 'server_type' in config:
            server_type = config.server_type
        else:
            server_type = EMAIL.SMTP.ServerType.Generic

        if not server_type:
            server_type = EMAIL.SMTP.ServerType.Generic

        # Only the generic kind speaks the SMTP protocol itself, so only it has a mode to map
        if server_type == EMAIL.SMTP.ServerType.Generic:
            config.mode_outbox = _modes[config.mode]

        class_ = self._impl_class[server_type]
        instance = class_(config, config_no_sensitive, self.audit_log)

        return instance

# ################################################################################################################################
# ################################################################################################################################
