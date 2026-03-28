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

    class SimpleIO:
        output_optional = 'status',
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        statuses = store.get_user_statuses()

        self.response.payload[:] = [{'status': s} for s in statuses]

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    name = 'file-transfer.user-status.create'

    class SimpleIO:
        input_required = 'status',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.add_user_status(self.request.input.status)

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.user-status.delete'

    class SimpleIO:
        input_required = 'status',

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        store.remove_user_status(self.request.input.status)

# ################################################################################################################################
# ################################################################################################################################
