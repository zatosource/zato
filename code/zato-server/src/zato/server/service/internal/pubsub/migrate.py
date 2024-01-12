# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class MigrateDeliveryServer(AdminService):
    """ Synchronously notifies all servers that a migration is in progress for input sub_key, then stops a delivery task
    on current server and starts it on another one.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key', 'new_delivery_server_name', 'endpoint_type')

# ################################################################################################################################

    def handle(self):

        # Local aliases
        sub_key = self.request.input.sub_key
        new_delivery_server_name = self.request.input.new_delivery_server_name
        endpoint_type = self.request.input.endpoint_type

        # Get a PubSubTool for this sub_key ..
        pub_sub_tool = self.pubsub.pubsub_tool_by_sub_key[sub_key]

        # .. and find a particular delivery for this very sub key.
        task = pub_sub_tool.get_delivery_task(sub_key)

        self.logger.info('About to migrate delivery task for sub_key `%s` (%s) to server `%s`',
            sub_key, endpoint_type, new_delivery_server_name)

        # First, let other servers know that this sub_key is no longer being handled.
        # We do it synchronously to make sure that they do not send anything to us anymore.
        reply = self.server.rpc.invoke_all('zato.pubsub.migrate.notify-delivery-task-stopping', {
            'sub_key': sub_key,
            'endpoint_type': endpoint_type,
            'new_delivery_server_name': new_delivery_server_name,
        })

        if reply.is_ok:
            self.logger.warning('Could not notify other servers of a stopping delivery task, e:`%s`', reply)
            return

        # Stop the task before proceeding to make sure this task will handle no new messages
        task.stop()

        # Clear any in-progress messages out of RAM. Note that any non-GD remaining messages
        # will be lost but GD are in SQL anyway so they will be always available on the new server.
        task.clear()

        # We can remove this task from its pubsub_tool so as to release some memory
        pub_sub_tool.remove_sub_key(sub_key)

        # We can let the new server know it can start its task for sub_key
        self.logger.info('Notifying server `%s` to start delivery task for `%s` (%s)', new_delivery_server_name,
                sub_key, endpoint_type)

        # Name of the service we are to invoke
        service_name = 'zato.pubsub.delivery.create-delivery-task'

        # Try to look up that subscription ..
        sub = self.pubsub.get_subscription_by_sub_key(sub_key)

        # .. create a new task if the subscription exists ..
        if sub:
            invoker = self.server.rpc.get_invoker_by_server_name(new_delivery_server_name)
            invoker.invoke(service_name, {
                'sub_key': sub_key,
                'endpoint_type': endpoint_type,
                'task_delivery_interval': sub.task_delivery_interval
            })

        # .. or log an exception otherwise.
        else:
            msg = 'Could not find sub_key `%s` to invoke service `%s` with'
            self.logger.info(msg, sub_key, service_name)

# ################################################################################################################################

class NotifyDeliveryTaskStopping(AdminService):
    """ Invoked when a delivery task is about to stop - deletes from pubsub information about input sub_key's delivery task.
    Thanks to this, when a message is published and there is no new delivery task running yet, this message will be queued up
    instead of being delivered to a task that is about to stop. The new task will pick it up when it has started up.
    """
    class SimpleIO:
        input_required = ('sub_key', 'endpoint_type')

    def handle(self):
        self.pubsub.delete_sub_key_server(self.request.input.sub_key)

# ################################################################################################################################
