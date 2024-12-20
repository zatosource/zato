# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest
from zato.common.json_internal import dumps
from zato.common.pubsub import HandleNewMessageCtx
from zato.common.util.pubsub import is_service_subscription
from zato.server.pubsub.delivery.tool import PubSubTool
from zato.server.service import Int, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

if 0:
    from zato.common.pubsub import PubSubMessage
    from zato.common.typing_ import any_, anydict, callable_, strcalldict, strdict
    from zato.server.connection.http_soap.outgoing import RESTWrapper
    from zato.server.pubsub.model import Subscription
    anydict = anydict
    PubSubMessage = PubSubMessage
    Subscription = Subscription

# ################################################################################################################################

class NotifyPubSubMessage(AdminService):
    """ Notifies pubsub about new messages available. It is guaranteed that this service will be always invoked
    on the server where each sub_key from sub_key_list exists.
    """
    def handle(self):
        # The request that we have on input needs to be sent to a pubsub_tool for each sub_key,
        # even if it is possibly the same pubsub_tool for more than one input sub_key.
        raw_request = self.request.raw_request # type: anydict
        req = raw_request['request']

        for sub_key in req['sub_key_list']:
            pubsub_tool = self.pubsub.pubsub_tool_by_sub_key[sub_key]
            pubsub_tool.handle_new_messages(HandleNewMessageCtx(self.cid, req['has_gd'], [sub_key],
                req['non_gd_msg_list'], req['is_bg_call'], req['pub_time_max']))

# ################################################################################################################################

class CreateDeliveryTask(AdminService):
    """ Starts a new delivery task for endpoints other than WebSockets (which are handled separately).
    """
    def handle(self):
        config = self.request.raw_request # type: anydict

        # Creates a pubsub_tool that will handle this subscription and registers it with pubsub
        pubsub_tool = PubSubTool(self.pubsub, self.server, config['endpoint_type'])

        # Makes this sub_key known to pubsub but only if this is not a service subscription
        # because subscriptions of this sort are handled by the worker store directly in init_pubsub.
        if not is_service_subscription(config):
            pubsub_tool.add_sub_key(config['sub_key'])

        # Common message for both local server and broker
        msg = {
            'cluster_id': self.server.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'sub_key': config['sub_key'],
            'endpoint_type': config['endpoint_type'],
            'task_delivery_interval': config['task_delivery_interval'],
            'source': 'delivery.CreateDeliveryTask',
            'source_server_name': self.server.name,
            'source_server_pid': self.server.pid,
        }

        # Update in-RAM state of workers
        msg['action'] = BROKER_MSG_PUBSUB.SUB_KEY_SERVER_SET.value
        self.broker_client.publish(msg)

# ################################################################################################################################

class DeliverMessage(AdminService):
    """ Callback service invoked by delivery tasks for each message or a list of messages that need to be delivered
    to a given endpoint.
    """
    class SimpleIO(AdminSIO):
        input_required:'any_' = (Opaque('msg'), Opaque('subscription'))

# ################################################################################################################################

    def handle(self) -> 'None':
        msg = self.request.input.msg # type: any_

        subscription = self.request.input.subscription # type: Subscription
        endpoint_impl_getter = self.pubsub.get_endpoint_impl_getter(subscription.config['endpoint_type']) # type: callable_

        func = deliver_func[subscription.config['endpoint_type']] # type: callable_
        func(self, msg, subscription, endpoint_impl_getter)

# ################################################################################################################################

    def _get_data_from_message(self, msg:'any_') -> 'any_':

        # A list of messages is given on input so we need to serialize each of them individually
        if isinstance(msg, list):
            out:'any_' = []
            for elem in msg: # type: ignore
                out.append(elem.serialized if elem.serialized else elem.to_external_dict())
            return out

        # A single message was given on input
        else:
            return msg.serialized if msg.serialized else msg.to_external_dict()

# ################################################################################################################################

    def _deliver_rest(self,
        msg:'list[PubSubMessage]',
        sub:'Subscription',
        impl_getter:'callable_',
        ) -> 'None':

        # Local variables
        out_http_method  = sub.config['out_http_method']
        out_http_soap_id = sub.config.get('out_http_soap_id')

        if not out_http_soap_id:
            raise ValueError('Missing out_http_soap_id for subscription `{}`'.format(sub))
        else:
            # Extract the actual data from the pub/sub message ..
            data = self._get_data_from_message(msg)

            # .. the outgoing connection's configuration ..
            rest_config:'strdict' = impl_getter(out_http_soap_id)

            # .. from which we can extract the actual wrapper ..
            conn:'RESTWrapper' = rest_config['conn']

            # .. make sure that we send JSON ..
            if not isinstance(data, str):
                data = dumps(data)

            # .. which now can be invoked.
            _ = conn.http_request(out_http_method, self.cid, data=data)

# ################################################################################################################################

    def _deliver_amqp(
        self,
        msg:'PubSubMessage',
        sub:'Subscription',
        _ignored_impl_getter # type: ignore
    ) -> 'None':

        # Ultimately we should use impl_getter to get the outconn
        for value in self.server.worker_store.worker_config.out_amqp.values(): # type: ignore
            if value['config']['id'] == sub.config['out_amqp_id']:

                data = self._get_data_from_message(msg)
                name:'str' = value['config']['name']
                kwargs = {}

                if sub.config['amqp_exchange']:
                    kwargs['exchange'] = sub.config['amqp_exchange']

                if sub.config['amqp_routing_key']:
                    kwargs['routing_key'] = sub.config['amqp_routing_key']

                self.outgoing.amqp.send(dumps(data), name, **kwargs)

                # We found our outconn and the message was sent, we can stop now
                break

# ################################################################################################################################

    def _deliver_wsx(self, msg, sub, _ignored_impl_getter) -> 'None': # type: ignore
        raise NotImplementedError('WSX deliveries should be handled by each socket\'s deliver_pubsub_msg')

# ################################################################################################################################

    def _deliver_srv(self, msg:'any_', sub:'Subscription', _ignored_impl_getter:'any_') -> 'None':

        # Reusable
        is_list = isinstance(msg, list)

        #
        # We can have two cases.
        #
        # 1) The messages were published via self.pubsub.publish('service.name')
        # 2) The messages were published to a topic and one of its subscribers is a service
        #
        # Depending on which case it is, we will extract the actual service's name differently.
        #

        # We do not know upfront which case it will be so this needs to be extracted upfront.
        # Each message will be destinated for the same service so we can extract the target service's name
        # from the first message in list, assuming it is in a list at all.
        zato_ctx:'any_' = msg[0].zato_ctx if is_list else msg.zato_ctx

        #
        # Case 1) is where we can find the service name immediately.
        #
        target_service_name = zato_ctx != '{}' and zato_ctx.get('target_service_name')

        #
        # Case 2) is where we need to look up the service's name based on a given endpoint that points to the service.
        #
        if not target_service_name:
            endpoint = self.pubsub.get_endpoint_by_id(sub.endpoint_id)
            target_service_name = self.server.service_store.get_service_name_by_id(endpoint.service_id)

        # Invoke the target service, giving it on input everything that we have,
        # regardless of whether it is a list or not.
        self.invoke(target_service_name, msg)

# ################################################################################################################################

# We need to register it here because it refers to DeliverMessage's methods
deliver_func:'strcalldict' = {
    PUBSUB.ENDPOINT_TYPE.REST.id: DeliverMessage._deliver_rest,
    PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id: DeliverMessage._deliver_wsx,
    PUBSUB.ENDPOINT_TYPE.SERVICE.id: DeliverMessage._deliver_srv,
}

# ################################################################################################################################

class GetServerPIDForSubKey(AdminService):
    """ Returns PID of a server process for input sub_key.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key',)
        output_optional:'any_' = (Int('server_pid'),)

# ################################################################################################################################

    def _raise_bad_request(self, sub_key:'str') -> 'None':
        raise BadRequest(self.cid, 'No such sub_key found `{}`'.format(sub_key))

# ################################################################################################################################

    def handle(self) -> 'None':
        sub_key = self.request.input.sub_key
        try:
            server = self.pubsub.get_delivery_server_by_sub_key(sub_key, needs_lock=False)
        except KeyError:
            self._raise_bad_request(sub_key)
        else:
            if server:
                self.response.payload.server_pid = server.server_pid
            else:
                self._raise_bad_request(sub_key)

# ################################################################################################################################
