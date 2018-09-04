# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns all delivery servers defined for cluster.
    """
    name = 'pubsub.task.delivery-server.get-list'

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id',)
        output_required = ('name', 'pid', AsIs('thread_id'), AsIs('object_id'), 'is_active', 'sub_keys', 'topics', 'messages')
        output_optional = ('last_sync', 'last_delivery')
        output_repeated = True
        output_elem = None

    def get_data(self):
        return [
            {'name':'ZZZ', 'pid':'1101', 'thread_id':'DummyThread-46', 'object_id':'0x7f4ca8380690', 'is_active':True,
             'sub_keys': 11, 'topics':1, 'messages':391,
             'last_sync':'2018-09-03T10:49:00.431767', 'last_delivery':'2018-09-03T10:49:00.97212'
             },

            {'name':'QQQ', 'pid':'2341', 'thread_id':'DummyThread-39', 'object_id':'0x7f4ca83b1b40', 'is_active':False,
             'sub_keys': 43, 'topics':39, 'messages': 5,
             'last_sync':'2018-08-21T15:17:07.014784', 'last_delivery':'2018-08-30T11:19:45.09732'},
        ]

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
