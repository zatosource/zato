# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HTTP_SOAP_SERIALIZATION_TYPE, PUBSUB, URL_TYPE
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest
from zato.common.pubsub import HandleNewMessageCtx
from zato.server.pubsub.task import PubSubTool
from zato.common.json_internal import dumps
from zato.server.service import Int, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

if 0:
    from zato.common.pubsub import PubSubMessage
    from zato.common.typing_ import any_, anydict, callable_
    from zato.server.pubsub.model import Subscription

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

        # Makes this sub_key known to pubsub
        pubsub_tool.add_sub_key(config['sub_key'])

        # Common message for both local server and broker
        msg = {
            'cluster_id': self.server.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'sub_key': config['sub_key'],
            'endpoint_type': config['endpoint_type'],
            'task_delivery_interval': config['task_delivery_interval'],
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
        input_required = (Opaque('msg'), Opaque('subscription'))

# ################################################################################################################################

    def handle(self) -> 'None':
        msg = self.request.input.msg # type: any_

        subscription = self.request.input.subscription # type: Subscription
        endpoint_impl_getter = self.pubsub.endpoint_impl_getter[subscription.config['endpoint_type']] # type: callable_

        func = deliver_func[subscription.config['endpoint_type']] # type: callable_
        func(self, msg, subscription, endpoint_impl_getter)

# ################################################################################################################################

    def _get_data_from_message(self, msg:'any_') -> 'any_':

        # A list of messages is given on input so we need to serialize each of them individually
        if isinstance(msg, list):
            out = []
            for elem in msg:
                out.append(elem.serialized if elem.serialized else elem.to_external_dict())
            return out
        # A single message was given on input
        else:
            return msg.serialized if msg.serialized else msg.to_external_dict()

# ################################################################################################################################

    def _deliver_rest_soap(self,
        msg:'list[PubSubMessage]',
        subscription:'Subscription',
        impl_getter:'callable_',
        _suds:'str'=HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id,
        _rest:'str'=URL_TYPE.PLAIN_HTTP
        ) -> 'None':

        if not subscription.config['out_http_soap_id']:
            raise ValueError('Missing out_http_soap_id for subscription `{}`'.format(subscription))
        else:
            data = self._get_data_from_message(msg)
            http_soap = impl_getter(subscription.config['out_http_soap_id']) # type: any_

            _is_rest = http_soap['config']['transport'] == _rest # type: bool
            _has_suds = http_soap['config']['serialization_type'] == _suds # type: bool

            # If it is REST or a suds-based connection, we can just invoke it directly
            if _is_rest or (not _has_suds):
                http_soap.conn.http_request(subscription.config['out_http_method'], self.cid, data=data)

            # .. while suds-based outgoing connections need to invoke the hook service which will
            # in turn issue a SOAP request to the remote server.
            else:
                self.pubsub.invoke_on_outgoing_soap_invoke_hook(msg, subscription, http_soap)

# ################################################################################################################################

    def _deliver_amqp(
        self,
        msg:'PubSubMessage',
        subscription:'Subscription',
        _ignored_impl_getter # type: ignore
    ) -> 'None':

        # Ultimately we should use impl_getter to get the outconn
        for value in self.server.worker_store.worker_config.out_amqp.values():
            if value['config']['id'] == subscription.config['out_amqp_id']:

                data = self._get_data_from_message(msg)
                name = value['config']['name']
                kwargs = {}

                if subscription.config['amqp_exchange']:
                    kwargs['exchange'] = subscription.config['amqp_exchange']

                if subscription.config['amqp_routing_key']:
                    kwargs['routing_key'] = subscription.config['amqp_routing_key']

                self.outgoing.amqp.send(dumps(data), name, **kwargs)

                # We found our outconn and the message was sent, we can stop now
                break

# ################################################################################################################################

    def _deliver_wsx(self, msg, subscription, _ignored_impl_getter) -> 'None': # type: ignore
        raise NotImplementedError('WSX deliveries should be handled by each socket\'s deliver_pubsub_msg')

# ################################################################################################################################

    def _deliver_srv(self, msg:'any_', subscription:'Subscription', _ignored_impl_getter:'any_') -> 'None':

        # Reusable
        is_list = isinstance(msg, list)

        # Each message will be destinated for the same service so we can extract the target service's name
        # from the first message in list, assuming it is in a list at all.
        zato_ctx = msg[0].zato_ctx if is_list else msg.zato_ctx
        target_service_name = zato_ctx['target_service_name']

        # Invoke the target service, giving it on input everything that we had,
        # do it either for each message from the list ..
        if is_list:
            for item in msg: # type: PubSubMessage
                self.invoke(target_service_name, item)
        else:
            # .. or directly, if input is not a list
            self.invoke(target_service_name, msg)

# ################################################################################################################################

# We need to register it here because it refers to DeliverMessage's methods
deliver_func = {
    PUBSUB.ENDPOINT_TYPE.AMQP.id: DeliverMessage._deliver_amqp,
    PUBSUB.ENDPOINT_TYPE.REST.id: DeliverMessage._deliver_rest_soap,
    PUBSUB.ENDPOINT_TYPE.SOAP.id: DeliverMessage._deliver_rest_soap,
    PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id: DeliverMessage._deliver_wsx,
    PUBSUB.ENDPOINT_TYPE.SERVICE.id: DeliverMessage._deliver_srv,
}

# ################################################################################################################################

class GetServerPIDForSubKey(AdminService):
    """ Returns PID of a server process for input sub_key.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key',)
        output_optional = (Int('server_pid'),)

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
