# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.config_pubsub_system_perf import Service_Count, Service_Name_Template
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# This file is hot-deployed into the test Zato server by conftest.py.
# It defines the 500 receiver services that push subscriptions deliver into,
# each counting its receptions, plus the harness services the test invokes.

# Per-service reception counters, keyed by full service name
_received_counts = {}

# ################################################################################################################################
# ################################################################################################################################

def _make_receiver_handle(service_name:'str') -> 'object':
    """ Builds a handle method that counts one reception for its service.
    """
    def handle(self:'Service') -> 'None':
        _received_counts[service_name] += 1

    return handle

# ################################################################################################################################

# .. dynamically create all the receiver service classes ..

for _index in range(1, Service_Count + 1):

    _full_service_name = Service_Name_Template.format(_index)
    _class_name = f'SystemPerfReceiver{_index:04d}'

    _received_counts[_full_service_name] = 0

    _cls = type(_class_name, (Service,), {
        'name': _full_service_name,
        'handle': _make_receiver_handle(_full_service_name),
    })

    globals()[_class_name] = _cls

# ################################################################################################################################
# ################################################################################################################################

class SystemPerfGetReceived(Service):
    """ Returns the reception totals collected by the receiver services so far.
    """

    name = 'test.system.perf.get-received'

    def handle(self) -> 'None':
        from json import dumps

        total = sum(_received_counts.values())

        services_with_data = 0
        for count in _received_counts.values():
            if count:
                services_with_data += 1

        out = {
            'total': total,
            'services_with_data': services_with_data,
        }

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class SystemPerfClearReceived(Service):
    """ Resets all the reception counters to zero.
    """

    name = 'test.system.perf.clear-received'

    def handle(self) -> 'None':
        for service_name in _received_counts:
            _received_counts[service_name] = 0

# ################################################################################################################################
# ################################################################################################################################

class SystemPerfStopDelivery(Service):
    """ Stops every push delivery greenlet so a backlog can build up.
    """

    name = 'test.system.perf.stop-delivery'

    def handle(self) -> 'None':
        sub_keys = list(self.server.config_manager._push_subs)

        for sub_key in sub_keys:
            self.server.pubsub_push_delivery.stop_sub_key(sub_key)

# ################################################################################################################################
# ################################################################################################################################

class SystemPerfStartDelivery(Service):
    """ Restarts the push delivery greenlets so the accumulated backlog drains.
    """

    name = 'test.system.perf.start-delivery'

    def handle(self) -> 'None':
        sub_keys = list(self.server.config_manager._push_subs)

        for sub_key in sub_keys:
            self.server.pubsub_push_delivery.start_sub_key(sub_key)

# ################################################################################################################################
# ################################################################################################################################

class SystemPerfPublish(Service):
    """ Publishes a message through the service facade (self.pubsub.publish),
    exercising the second user-facing publish path next to the REST channel.
    """

    name = 'test.system.perf.publish'

    def handle(self) -> 'None':
        from json import dumps

        topic_name = self.request.raw_request['topic_name']
        data = self.request.raw_request['data']

        result = self.pubsub.publish(topic_name, data)

        out = {
            'msg_id': result.msg_id,
        }

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################
