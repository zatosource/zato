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

# Zato
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
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
