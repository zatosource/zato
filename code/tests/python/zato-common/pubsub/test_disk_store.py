# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
import unittest

# cryptography
from cryptography.fernet import Fernet

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.disk_store import DiskMessageStore

# ################################################################################################################################
# ################################################################################################################################

class TestDiskMessageStore(unittest.TestCase):

    def setUp(self) -> 'None':
        self.test_dir = tempfile.mkdtemp()
        self.store = DiskMessageStore(self.test_dir)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        shutil.rmtree(self.test_dir)

# ################################################################################################################################

    def test_store_creates_file(self) -> 'None':
        """ Test that storing a message creates a file on disk.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'
        data = 'Hello world'
        data_class = ''

        data_ref = self.store.store(message_id, topic_name, data, data_class)

        absolute_path = os.path.join(self.test_dir, data_ref)
        self.assertTrue(os.path.exists(absolute_path))

# ################################################################################################################################

    def test_store_and_load_roundtrip(self) -> 'None':
        """ Test that data survives a store/load roundtrip.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'
        data = '{"customer_id": 42, "action": "created"}'
        data_class = 'myapp.models.Customer'

        data_ref = self.store.store(message_id, topic_name, data, data_class)
        result = self.store.load(data_ref)

        self.assertEqual(result.data, data)
        self.assertEqual(result.data_class, data_class)

# ################################################################################################################################

    def test_store_and_load_multiline_data(self) -> 'None':
        """ Test that multi-line payloads are preserved.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'
        data = '{"customer_id": 42,\n "action": "created",\n "details": "long text here"}'
        data_class = ''

        data_ref = self.store.store(message_id, topic_name, data, data_class)
        result = self.store.load(data_ref)

        self.assertEqual(result.data, data)

# ################################################################################################################################

    def test_store_and_load_empty_data(self) -> 'None':
        """ Test that empty data is handled correctly.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'
        data = ''
        data_class = ''

        data_ref = self.store.store(message_id, topic_name, data, data_class)
        result = self.store.load(data_ref)

        self.assertEqual(result.data, data)

# ################################################################################################################################

    def test_store_and_load_data_with_equals_sign(self) -> 'None':
        """ Test that data containing equals signs is preserved.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'
        data = 'key1=value1\nkey2=value2'
        data_class = ''

        data_ref = self.store.store(message_id, topic_name, data, data_class)
        result = self.store.load(data_ref)

        self.assertEqual(result.data, data)

# ################################################################################################################################

    def test_delete_removes_file(self) -> 'None':
        """ Test that deleting a message removes its file.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'
        data = 'test data'
        data_class = ''

        data_ref = self.store.store(message_id, topic_name, data, data_class)

        absolute_path = os.path.join(self.test_dir, data_ref)
        self.assertTrue(os.path.exists(absolute_path))

        self.store.delete(data_ref)

        self.assertFalse(os.path.exists(absolute_path))

# ################################################################################################################################

    def test_delete_nonexistent_does_not_raise(self) -> 'None':
        """ Test that deleting a nonexistent file does not raise.
        """
        self.store.delete('nonexistent/ab/cd/zpsm.fake.msg')

# ################################################################################################################################

    def test_sharding_uses_hex_part(self) -> 'None':
        """ Test that the directory sharding uses the hex portion of the message ID.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'

        data_ref = self.store._make_ref(message_id, topic_name)

        # .. the hex part is 'abcdef1234567890', so shard dirs should be 'ab' and 'cd' ..
        self.assertIn('ab', data_ref)
        self.assertIn('cd', data_ref)
        self.assertTrue(data_ref.startswith('test.topic/'))
        self.assertTrue(data_ref.endswith('.msg'))

# ################################################################################################################################

    def test_different_ids_get_different_shards(self) -> 'None':
        """ Test that different message IDs can produce different shard directories.
        """
        message_id_1 = 'zpsm.20260517-113200-1234-abcdef1234567890'
        message_id_2 = 'zpsm.20260517-113200-1234-xyzcde1234567890'
        topic_name = 'test.topic'

        ref_1 = self.store._make_ref(message_id_1, topic_name)
        ref_2 = self.store._make_ref(message_id_2, topic_name)

        self.assertNotEqual(ref_1, ref_2)

# ################################################################################################################################

    def test_file_format_is_key_value(self) -> 'None':
        """ Test that the file on disk contains key=value lines.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.topic'
        data = 'test payload'
        data_class = 'myapp.models.Order'

        data_ref = self.store.store(message_id, topic_name, data, data_class)

        absolute_path = os.path.join(self.test_dir, data_ref)

        with open(absolute_path, 'r', encoding='utf-8') as file_handle:
            content = file_handle.read()

        lines = content.split('\n')

        self.assertEqual(lines[0], '_version=1')
        self.assertEqual(lines[1], f'msg_id={message_id}')
        self.assertEqual(lines[2], f'topic_name={topic_name}')
        self.assertEqual(lines[3], f'data_class={data_class}')
        self.assertEqual(lines[4], f'data={data}')

# ################################################################################################################################

    def test_rename_topic_dir(self) -> 'None':
        """ Test that renaming a topic directory moves the files.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        old_topic = 'old.topic'
        new_topic = 'new.topic'
        data = 'test data'

        data_ref = self.store.store(message_id, old_topic, data, '')

        # .. the file should exist under old topic ..
        old_path = os.path.join(self.test_dir, data_ref)
        self.assertTrue(os.path.exists(old_path))

        # .. rename the directory ..
        self.store.rename_topic_dir(old_topic, new_topic)

        # .. old directory should be gone ..
        old_dir = os.path.join(self.test_dir, old_topic)
        self.assertFalse(os.path.exists(old_dir))

        # .. new directory should contain the file ..
        new_ref = data_ref.replace(f'{old_topic}/', f'{new_topic}/', 1)
        new_path = os.path.join(self.test_dir, new_ref)
        self.assertTrue(os.path.exists(new_path))

# ################################################################################################################################

    def test_rename_topic_dir_nonexistent(self) -> 'None':
        """ Test that renaming a nonexistent topic directory does not raise.
        """
        self.store.rename_topic_dir('nonexistent.topic', 'new.topic')

# ################################################################################################################################

    def test_delete_topic_dir(self) -> 'None':
        """ Test that deleting a topic directory removes all files.
        """
        topic_name = 'delete.me'

        message_id_1 = 'zpsm.20260517-113200-1234-abcdef1234567890'
        message_id_2 = 'zpsm.20260517-113200-1234-11223344aabbccdd'

        _ = self.store.store(message_id_1, topic_name, 'data one', '')
        _ = self.store.store(message_id_2, topic_name, 'data two', '')

        topic_dir = os.path.join(self.test_dir, topic_name)
        self.assertTrue(os.path.exists(topic_dir))

        self.store.delete_topic_dir(topic_name)

        self.assertFalse(os.path.exists(topic_dir))

# ################################################################################################################################

    def test_delete_topic_dir_nonexistent(self) -> 'None':
        """ Test that deleting a nonexistent topic directory does not raise.
        """
        self.store.delete_topic_dir('nonexistent.topic')

# ################################################################################################################################
# ################################################################################################################################

class TestDiskMessageStoreEncryption(unittest.TestCase):

    def setUp(self) -> 'None':
        self.test_dir = tempfile.mkdtemp()
        self.crypto_manager = CryptoManager.from_secret_key(secret_key=Fernet.generate_key())
        self.store = DiskMessageStore(self.test_dir, crypto_manager=self.crypto_manager)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        shutil.rmtree(self.test_dir)

# ################################################################################################################################

    def test_encrypted_store_and_load_roundtrip(self) -> 'None':
        """ Test that encrypted data survives a store/load roundtrip.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.encrypted'
        data = '{"customer_id": 42, "action": "created"}'
        data_class = 'myapp.models.Customer'

        data_ref = self.store.store(message_id, topic_name, data, data_class, encrypt=True)
        result = self.store.load(data_ref)

        self.assertEqual(result.data, data)
        self.assertEqual(result.data_class, data_class)

# ################################################################################################################################

    def test_encrypted_file_contains_encrypted_header(self) -> 'None':
        """ Test that an encrypted file has encrypted=true in its header.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.encrypted'
        data = 'plaintext payload'

        data_ref = self.store.store(message_id, topic_name, data, '', encrypt=True)

        absolute_path = os.path.join(self.test_dir, data_ref)

        with open(absolute_path, 'r', encoding='utf-8') as file_handle:
            content = file_handle.read()

        self.assertIn('encrypted=true', content)

        # .. the raw data= value should NOT contain the plaintext ..
        lines = content.split('\n')
        data_line = ''

        for line in lines:
            if line.startswith('data='):
                data_line = line[len('data='):]
                break

        self.assertNotEqual(data_line, data)
        self.assertTrue(data_line.startswith('gAAA'))

# ################################################################################################################################

    def test_encrypted_multiline_roundtrip(self) -> 'None':
        """ Test that multi-line data is preserved through encryption.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.encrypted'
        data = 'line one\nline two\nline three'

        data_ref = self.store.store(message_id, topic_name, data, '', encrypt=True)
        result = self.store.load(data_ref)

        self.assertEqual(result.data, data)

# ################################################################################################################################

    def test_unencrypted_file_still_loads(self) -> 'None':
        """ Test that a store with crypto_manager can still load unencrypted files.
        """
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        topic_name = 'test.plain'
        data = 'not encrypted'

        data_ref = self.store.store(message_id, topic_name, data, '', encrypt=False)
        result = self.store.load(data_ref)

        self.assertEqual(result.data, data)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
