# -*- coding: utf-8 -*-

# stdlib
from operator import itemgetter

# Zato
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log import LogContainer

    LogContainer = LogContainer

# ################################################################################################################################
# ################################################################################################################################

class GetEventList(AdminService):
    name = 'zato.audit-log.event.get-list'

    class SimpleIO:
        input_optional = 'cluster_id', 'type_', AsIs('object_id')
        output_optional = 'server_name', 'server_pid', 'type_', AsIs('object_id'), 'direction', 'timestamp', \
            AsIs('msg_id'), AsIs('event_id'), AsIs('conn_id'), 'in_reply_to', 'data', Int('data_len')

# ################################################################################################################################

    def handle(self):

        type_     = self.request.input.type_
        object_id = self.request.input.object_id

        result = self.server.audit_log.get_container(type_, object_id) # type: LogContainer
        if result:
            result = result.to_dict() # type: dict

            out = []

            for value in result.values(): # type: (str, list)
                for item in value: # type: dict
                    item['server_name'] = self.server.name
                    item['server_pid'] = self.server.pid
                    item['data_len'] = len(item['data']) if item['data'] is not None else 0
                    out.append(item)

            out.sort(key=itemgetter('timestamp'), reverse=True)
            self.response.payload[:] = out

# ################################################################################################################################
# ################################################################################################################################
