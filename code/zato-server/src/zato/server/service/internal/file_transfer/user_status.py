# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    name = 'file-transfer.user-status.get-list'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        statuses = store.get_user_statuses()
        self.response.payload = [{'status': s} for s in statuses]

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    name = 'file-transfer.user-status.create'

    def handle(self):
        input = self.request.raw_request or {}
        status = input.get('status')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.add_user_status(status)
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.user-status.delete'

    def handle(self):
        input = self.request.raw_request or {}
        status = input.get('status')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.remove_user_status(status)
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################
