# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from operator import itemgetter
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# Zato
from zato.common.api import EMAIL
from zato.server.connection.email import GenericIMAPConnection, Microsoft365IMAPConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.api import IMAPMessage
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Env_Key_IMAP_Host = 'Zato_Test_IMAP_Host'
    Env_Key_IMAP_Port = 'Zato_Test_IMAP_Port'
    Env_Key_IMAP_Username = 'Zato_Test_IMAP_Username'
    Env_Key_IMAP_Password = 'Zato_Test_IMAP_Password'
    Env_Key_IMAP_Test_Subject = 'Zato_Test_IMAP_Test_Subject'

    Env_Key_MS365_Tenant_ID = 'Zato_Test_IMAP_MS365_Tenant_ID'
    Env_Key_MS365_Client_ID = 'Zato_Test_IMAP_MS365_Client_ID'
    Env_Key_MS365_Secret = 'Zato_Test_IMAP_MS365_Secret'
    Env_Key_MS365_Resource = 'Zato_Test_IMAP_MS365_Resource'
    Env_Key_MS365_Test_Subject = 'Zato_Test_IMAP_MS365_Test_Subject'

# ################################################################################################################################
# ################################################################################################################################

class ExpectedGetData:
    msg_id: 'str'
    imap_message: 'IMAPMessage'
    body_plain: 'anylist'
    body_html: 'anylist'
    name: 'str'
    username: 'str'
    subject: 'str'
    sent_from_name: 'str'
    sent_from_email: 'str'
    sent_to_name: 'str'
    sent_to_email: 'str'
    cc: 'str | None'
    bcc: 'str | None'

# ################################################################################################################################
# ################################################################################################################################

class BaseIMAPConnectionTestCase(TestCase):

    def run_get_assertions(self, expected:'ExpectedGetData') -> 'None':

        self.assertTrue(len(expected.msg_id) > 1)
        self.assertEqual(expected.imap_message.data.subject, expected.subject)

        sent_from = expected.imap_message.data.sent_from[0]
        expected_sent_from = {
            'name': expected.sent_from_name,
            'email': expected.sent_from_email,
        }
        self.assertDictEqual(sent_from, expected_sent_from)

        sent_to = expected.imap_message.data.sent_to[0]
        expected_sent_to = {
            'name': expected.sent_to_name,
            'email': expected.sent_to_email,
        }
        self.assertDictEqual(sent_to, expected_sent_to)

        self.assertListEqual(expected.imap_message.data.cc, [])
        self.assertListEqual(expected.imap_message.data.bcc, [])

        body = expected.imap_message.data.body
        expected_body = {
            'plain': expected.body_plain,
            'html': expected.body_html,
        }
        self.assertDictEqual(body, expected_body)

        attachments = expected.imap_message.data.attachments
        attachments = sorted(attachments, key=itemgetter('filename'))

        # We expect for exactly two attachments to exist
        self.assertEqual(len(attachments), 2)

        attach1 = attachments[0]
        attach2 = attachments[1]

        self.assertEqual(attach1['content-type'], 'text/plain')
        self.assertEqual(attach1['size'], 5)
        self.assertEqual(attach1['filename'], 'file1.txt')

        self.assertEqual(attach2['content-type'], 'text/plain')
        self.assertEqual(attach2['size'], 5)
        self.assertEqual(attach2['filename'], 'file2.txt')

        attach1_content = attach1['content']
        attach1_content = attach1_content.getvalue()

        attach2_content = attach2['content']
        attach2_content = attach2_content.getvalue()

        self.assertEqual(attach1_content, b'data1')
        self.assertEqual(attach2_content, b'data2')

# ################################################################################################################################
# ################################################################################################################################

class GenericIMAPConnectionTestCase(BaseIMAPConnectionTestCase):

    def get_conn(self) -> 'GenericIMAPConnection | None':

        # Try to get the main environment variable ..
        host = os.environ.get(ModuleCtx.Env_Key_IMAP_Host)

        # .. and if it does not exist, do not run the test
        if not host:
            return
        else:
            port = os.environ.get(ModuleCtx.Env_Key_IMAP_Port)
            username = os.environ.get(ModuleCtx.Env_Key_IMAP_Username)
            password = os.environ.get(ModuleCtx.Env_Key_IMAP_Password)
            test_subject = os.environ.get(ModuleCtx.Env_Key_IMAP_Test_Subject)

        config = bunchify({
            'cluster_id': 1,
            'id': 2,
            'is_active':True,
            'opaque1':None,
            'name': 'My Name',
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'mode': EMAIL.IMAP.MODE.SSL,
            'debug_level': 2,
            'get_criteria': f'SUBJECT "{test_subject}"',
            'server_type': EMAIL.IMAP.ServerType.Generic,
        })

        conn = GenericIMAPConnection(config, config)
        return conn

# ################################################################################################################################

    def test_get(self):

        conn = self.get_conn()
        if not conn:
            return

        # Reusable
        test_subject = os.environ.get(ModuleCtx.Env_Key_IMAP_Test_Subject) or ''
        username = os.environ.get(ModuleCtx.Env_Key_IMAP_Username) or ''

        # Run the function under test
        result = conn.get()

        # Turn it to a list upfront
        result = list(result)

        # We expect to find one test message
        self.assertEqual(len(result), 1)

        # From now on, work with this message only
        result = result[0]

        msg_id, imap_message = result

        # Prepare the information about what we expect to receive ..

        expected = ExpectedGetData()

        expected.msg_id = msg_id
        expected.imap_message = imap_message
        expected.subject = test_subject

        expected.sent_from_name = ''
        expected.sent_from_email = username

        expected.sent_to_name = ''
        expected.sent_to_email = username

        expected.body_plain = ['This is a test message.']
        expected.body_html = []

        # .. and run assertions now.
        self.run_get_assertions(expected)

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365IMAPConnectionTestCase(BaseIMAPConnectionTestCase):

    def get_conn(self) -> 'Microsoft365IMAPConnection | None':

        # Try to get the main environment variable ..
        tenant_id = os.environ.get(ModuleCtx.Env_Key_MS365_Tenant_ID)

        # .. and if it does not exist, do not run the test
        if not tenant_id:
            return
        else:
            client_id = os.environ.get(ModuleCtx.Env_Key_MS365_Client_ID)
            secret = os.environ.get(ModuleCtx.Env_Key_MS365_Secret)
            resource = os.environ.get(ModuleCtx.Env_Key_MS365_Resource)

        config = {
            'cluster_id': 1,
            'id': 2,
            'is_active':True,
            'opaque1':None,
            'name': 'My Name',
            'tenant_id': tenant_id,
            'client_id': client_id,
            'password': secret,
            'username': resource,
            'filter_criteria': EMAIL.DEFAULT.FILTER_CRITERIA,
            'server_type': EMAIL.IMAP.ServerType.Microsoft365,
        }

        conn = Microsoft365IMAPConnection(config, config)
        return conn

# ################################################################################################################################

    def xtest_ping(self):

        conn = self.get_conn()
        if not conn:
            return

        # Assume we will not find the Inbox folder
        found_inbox = False

        # Run the function under test
        result = conn.ping()

        for item in result:
            if item.name == 'Inbox':
                found_inbox = True
                break

        if not found_inbox:
            self.fail(f'Expected for folder Inbox to exist among {result}')

# ################################################################################################################################

    def xtest_get(self):

        conn = self.get_conn()
        if not conn:
            return

        # Reusable
        test_subject = os.environ.get(ModuleCtx.Env_Key_MS365_Test_Subject)

        # Run the function under test
        result = conn.get()

        for item_id, item in result:

            if item.data.subject != test_subject:
                continue

            print(111, item_id)
            print(222, item.data.sent_from[0])
            print(333, item.data.subject)
            print(444, item.data.message_id)
            print(555, item.data)
            print()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
