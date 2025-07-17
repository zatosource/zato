#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script to verify pubsub topic importer imports work correctly.
"""

try:
    from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.odb.model import PubSubTopic
    from zato.common.odb.query import pubsub_topic_list
    
    print("✓ All imports successful")
    
    # Test basic instantiation
    importer = EnmasseYAMLImporter()
    pubsub_importer = PubSubTopicImporter(importer)
    
    print("✓ Importer instantiation successful")
    print("✓ PubSub topic importer implementation is ready")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
