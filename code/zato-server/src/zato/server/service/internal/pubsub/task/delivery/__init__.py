# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, GetListAdminSIO

class DeliveryTaskGetList(AdminService):
    """ Returns all delivery servers defined for cluster.
    """
    name = 'pubsub.task.get-list'

    class SimpleIO(GetListAdminSIO):
        input_required = 'cluster_id',
        output_required = ('server_name', 'server_pid', AsIs('thread_id'), AsIs('object_id'),
            'sub_key', 'topic_id', 'topic_name', Int('messages'))
        output_optional = 'last_sync', 'last_delivery', AsIs('ext_client_id')
        output_repeated = True
        output_elem = None

    def get_data(self):
        return [
            {'server_name':'ZZZ', 'server_pid':'1101',
             'thread_id':'DummyThread-183', 'object_id':'0x7f4ca83e68c0',
             'sub_key':'zpsk.wsx.32a358b555a4d2ec0f06b1cb', 'topic_id':1, 'topic_name':'/my/topic',
             'messages':39,
             'last_sync':'2018-09-03T10:49:00.431767', 'last_delivery':'2018-09-03T10:49:00.97212'
             },

            {'server_name':'QQQ', 'server_pid':'2341',
             'thread_id':'DummyThread-184', 'object_id':'0x7f4ca8380690',
             'sub_key':'zpsk.rest.bcb442f15ba7fa0765aa7d62', 'topic_id':1, 'topic_name':'/my/topic/2',
             'messages':1982,
             'last_sync':'2018-08-21T15:17:07.014784', 'last_delivery':'2018-08-30T11:19:45.09732',
             'ext_client_id':'RUID-3971'},
        ]

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
