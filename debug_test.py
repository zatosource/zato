#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code/zato-common/src'))

from zato.common.pubsub.matcher import PatternMatcher

# Mock PubSub constants
class MockPubSub:
    class API_Client:
        Publisher = 'publisher'
        Subscriber = 'subscriber'
        Publisher_Subscriber = 'publisher_subscriber'

# Test the specific failing case
def test_empty_segment_abuse():
    matcher = PatternMatcher()
    client_id = 'test-client-123'
    
    permissions = [
        {'pattern': 'admin.*.secret', 'access_type': MockPubSub.API_Client.Publisher},
        {'pattern': 'admin..secret', 'access_type': MockPubSub.API_Client.Subscriber}
    ]
    matcher.add_client(client_id, permissions)

    # Empty segment should match wildcard
    result = matcher.evaluate(client_id, 'admin..secret', 'publish')
    print(f"First test result: is_ok={result.is_ok}, reason={result.reason}")
    
    # Should also match exact empty pattern for subscribe
    result = matcher.evaluate(client_id, 'admin..secret', 'subscribe')
    print(f"Second test result: is_ok={result.is_ok}, reason={result.reason}")

if __name__ == '__main__':
    test_empty_segment_abuse()
