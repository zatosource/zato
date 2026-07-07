# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socketserver
import threading
from email.message import EmailMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import bytesnone, strdictlist, strdictlistnone, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IMAPTestRequestHandler(socketserver.StreamRequestHandler):
    """ Speaks just enough IMAP4 for imaplib-based clients to log in, select a folder, search for messages,
    fetch them, mark them as seen and log out.
    """

    def _respond(self, data:'bytes') -> 'None':
        self.wfile.write(data + b'\r\n')

# ################################################################################################################################

    def _handle_capability(self, tag:'str') -> 'bool':
        self._respond(b'* CAPABILITY IMAP4rev1')
        self._respond(tag.encode('utf-8') + b' OK CAPABILITY completed')
        return True

# ################################################################################################################################

    def _handle_select(self, tag:'str') -> 'bool':

        # The client is told how many messages the mailbox holds at this moment
        message_count = self.server.get_message_count()

        self._respond(f'* {message_count} EXISTS'.encode('utf-8'))
        self._respond(b'* 0 RECENT')
        self._respond(tag.encode('utf-8') + b' OK [READ-WRITE] SELECT completed')
        return True

# ################################################################################################################################

    def _handle_logout(self, tag:'str') -> 'bool':
        self._respond(b'* BYE IMAP test server signing off')
        self._respond(tag.encode('utf-8') + b' OK LOGOUT completed')
        return False

# ################################################################################################################################

    def _handle_uid_search(self, tag:'str', parts:'strlist') -> 'None':

        # Everything after "TAG UID SEARCH" forms the search criteria
        criteria = ' '.join(parts[3:]).upper()

        # The UNSEEN criteria narrows the results down to unseen messages, anything else returns all of them
        if 'UNSEEN' in criteria:
            uid_list = self.server.get_uid_list(unseen_only=True)
        else:
            uid_list = self.server.get_uid_list(unseen_only=False)

        joined = ' '.join(uid_list)

        self._respond(f'* SEARCH {joined}'.strip().encode('utf-8'))
        self._respond(tag.encode('utf-8') + b' OK UID SEARCH completed')

# ################################################################################################################################

    def _handle_uid_fetch(self, tag:'str', parts:'strlist') -> 'None':

        # The UID of the message to fetch comes right after "TAG UID FETCH"
        uid = parts[3]
        data = self.server.get_message_data(uid)

        # A message that does not exist results in an empty, yet successful, response
        if data is None:
            self._respond(tag.encode('utf-8') + b' OK UID FETCH completed')
            return

        # The message body goes out as an IMAP literal - the header line announces how many bytes follow,
        # the raw bytes come next and the closing parenthesis concludes the untagged response.
        data_length = len(data)
        header = f'* {uid} FETCH (UID {uid} BODY[] {{{data_length}}}'.encode('utf-8')

        self.wfile.write(header + b'\r\n')
        self.wfile.write(data)
        self.wfile.write(b')\r\n')

        self._respond(tag.encode('utf-8') + b' OK UID FETCH completed')

# ################################################################################################################################

    def _handle_uid_store(self, tag:'str', parts:'strlist') -> 'None':

        # The UID of the message to update comes right after "TAG UID STORE"
        uid = parts[3]

        # Everything that follows describes the flags to set
        flags = ' '.join(parts[4:]).upper()

        if 'SEEN' in flags:
            self.server.mark_seen(uid)

        self._respond(tag.encode('utf-8') + b' OK UID STORE completed')

# ################################################################################################################################

    def _handle_uid(self, tag:'str', parts:'strlist') -> 'bool':

        subcommand = parts[2].upper()

        if subcommand == 'SEARCH':
            self._handle_uid_search(tag, parts)

        elif subcommand == 'FETCH':
            self._handle_uid_fetch(tag, parts)

        elif subcommand == 'STORE':
            self._handle_uid_store(tag, parts)

        # Any other UID subcommand simply succeeds
        else:
            self._respond(tag.encode('utf-8') + b' OK UID completed')

        return True

# ################################################################################################################################

    def _handle_any_other(self, tag:'str', command:'str') -> 'bool':
        message = f'{tag} OK {command} completed'
        self._respond(message.encode('utf-8'))
        return True

# ################################################################################################################################

    def handle(self) -> 'None':

        # Send the greeting first, advertising capabilities so the client does not need to ask for them
        self._respond(b'* OK [CAPABILITY IMAP4rev1] IMAP test server ready')

        # Keep serving commands until the client logs out or disconnects
        while True:

            line = self.rfile.readline()

            # An empty read means the client disconnected
            if not line:
                break

            text = line.strip().decode('utf-8', errors='replace')

            # Ignore keep-alive empty lines
            if not text:
                continue

            # Every received command is recorded for tests to assert on
            self.server.received_commands.append(text)
            logger.info('IMAP test server received: %s', text)

            parts = text.split(' ')
            tag = parts[0]
            command = parts[1].upper()

            if command == 'CAPABILITY':
                should_continue = self._handle_capability(tag)

            elif command == 'SELECT':
                should_continue = self._handle_select(tag)

            elif command == 'UID':
                should_continue = self._handle_uid(tag, parts)

            elif command == 'LOGOUT':
                should_continue = self._handle_logout(tag)

            # LOGIN, NOOP, CLOSE and anything else simply succeed
            else:
                should_continue = self._handle_any_other(tag, command)

            if not should_continue:
                break

# ################################################################################################################################
# ################################################################################################################################

class IMAPTestServer(socketserver.ThreadingTCPServer):
    """ A minimal IMAP server listening on 127.0.0.1 on a random port, for use in live tests.
    It keeps an in-memory mailbox that tests can add messages to and inspect the seen state of.
    """
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self) -> 'None':

        # Binding to port 0 makes the operating system pick a random free port
        super().__init__(('127.0.0.1', 0), IMAPTestRequestHandler)

        self.received_commands = []
        self.host, self.port = self.server_address

        # The in-memory mailbox - a list of dicts with the uid, raw message bytes and the seen flag,
        # guarded by a lock because each client connection is served in its own thread.
        self.mailbox:'strdictlist' = []
        self.mailbox_lock = threading.Lock()
        self.next_uid = 1

# ################################################################################################################################

    def start(self) -> 'None':
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        logger.info('IMAP test server listening on %s:%s', self.host, self.port)

# ################################################################################################################################

    def stop(self) -> 'None':
        self.shutdown()
        self.server_close()

# ################################################################################################################################

    def add_message(
        self,
        sent_from:'str',
        sent_to:'str',
        subject:'str',
        body:'str',
        attachments:'strdictlistnone' = None,
        ) -> 'str':
        """ Builds an RFC822 message out of the input fields and appends it to the mailbox, returning its UID.
        Each attachment is a dict with the filename, content_type and payload keys, where payload is bytes.
        """

        # Build the actual message first ..
        message = EmailMessage()
        message['From'] = sent_from
        message['To'] = sent_to
        message['Subject'] = subject
        message.set_content(body)

        # .. optionally, turn it into a multipart message with the requested attachments ..
        if attachments:
            for attachment in attachments:
                content_type = attachment['content_type']
                maintype, subtype = content_type.split('/')
                message.add_attachment(
                    attachment['payload'], maintype=maintype, subtype=subtype, filename=attachment['filename'])

        data = message.as_bytes()

        # .. and append it to the mailbox under a new UID.
        with self.mailbox_lock:
            uid = str(self.next_uid)
            self.next_uid += 1
            self.mailbox.append({'uid': uid, 'data': data, 'seen': False})

        logger.info('IMAP test server added message uid=%s subject=%s', uid, subject)

        return uid

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Empties the mailbox and the log of received commands.
        """
        with self.mailbox_lock:
            self.mailbox = []

        self.received_commands = []

# ################################################################################################################################

    def is_seen(self, uid:'str') -> 'bool':
        """ Returns True if the message of the given UID was marked as seen.
        """
        with self.mailbox_lock:
            for message in self.mailbox:
                if message['uid'] == uid:
                    out = message['seen']
                    break
            else:
                out = False

        return out

# ################################################################################################################################

    def mark_seen(self, uid:'str') -> 'None':
        with self.mailbox_lock:
            for message in self.mailbox:
                if message['uid'] == uid:
                    message['seen'] = True
                    break

# ################################################################################################################################

    def get_message_count(self) -> 'int':
        with self.mailbox_lock:
            out = len(self.mailbox)

        return out

# ################################################################################################################################

    def get_uid_list(self, unseen_only:'bool') -> 'strlist':
        """ Returns the UIDs of the messages in the mailbox, optionally narrowed down to the unseen ones.
        """
        out = []

        with self.mailbox_lock:
            for message in self.mailbox:
                if unseen_only:
                    if message['seen']:
                        continue
                out.append(message['uid'])

        return out

# ################################################################################################################################

    def get_message_data(self, uid:'str') -> 'bytesnone':
        """ Returns the raw bytes of the message of the given UID or None if there is no such message.
        """
        with self.mailbox_lock:
            for message in self.mailbox:
                if message['uid'] == uid:
                    out = message['data']
                    break
            else:
                out = None

        return out

# ################################################################################################################################

    def has_received(self, command:'str') -> 'bool':
        """ Returns True if any of the received lines contains the given IMAP command.
        """
        for line in self.received_commands:
            if command in line.upper():
                out = True
                break
        else:
            out = False

        return out

# ################################################################################################################################
# ################################################################################################################################
