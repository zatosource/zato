# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand
from zato.common.api import ZATO_INFO_FILE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class _PubSubCommand(ZatoCommand):
    """ Base class for all pub/sub CLI commands.
    """
    file_needed = ZATO_INFO_FILE
    needs_secrets_confirm = False

    def _get_client(self, args:'any_') -> 'any_':

        # Zato
        from zato.common.util.api import get_client_from_server_conf

        out = get_client_from_server_conf(args.path, stdin_data=self.stdin_data)
        return out

    def _print_header(self, label:'str') -> 'None':

        # colorama
        from colorama import Fore, Style

        print(f'{Fore.CYAN}{label}{Style.RESET_ALL}')

    def _print_field(self, label:'str', value:'any_') -> 'None':

        # colorama
        from colorama import Fore, Style

        print(f'  {Fore.CYAN}{label}:{Style.RESET_ALL} {Fore.WHITE}{value}{Style.RESET_ALL}')

    def _print_success(self, message:'str') -> 'None':

        # colorama
        from colorama import Fore, Style

        print(f'{Fore.GREEN}{message}{Style.RESET_ALL}')

    def _print_error(self, message:'str') -> 'None':

        # colorama
        from colorama import Fore, Style

        print(f'{Fore.RED}{message}{Style.RESET_ALL}')

    def _print_msg_id(self, msg_id:'str') -> 'None':

        # colorama
        from colorama import Fore, Style

        print(f'  {Fore.CYAN}msg_id:{Style.RESET_ALL} {Fore.YELLOW}{msg_id}{Style.RESET_ALL}')

    def _print_count(self, label:'str', count:'any_') -> 'None':

        # colorama
        from colorama import Fore, Style

        print(f'  {Fore.CYAN}{label}:{Style.RESET_ALL} {Fore.MAGENTA}{count}{Style.RESET_ALL}')

# ################################################################################################################################
# ################################################################################################################################

class Publish(_PubSubCommand):
    """ Publishes a message to a topic.

Examples:
  zato pubsub publish /path/to/server --topic /my/topic --data '{"order_id": 123}'
  zato pubsub publish /path/to/server --topic /events/user.created --data 'Hello' --priority 7 --expiration 3600000
    """

    opts = [
        {'name':'--topic', 'help':'Topic name to publish to'},
        {'name':'--data', 'help':'Message payload'},
        {'name':'--priority', 'help':'Message priority (1-9, default 5)'},
        {'name':'--expiration', 'help':'Expiration in milliseconds'},
    ]

    def execute(self, args:'any_') -> 'None':

        # stdlib
        import json

        client = self._get_client(args)

        payload:'anydict' = {
            'topic_name': args.topic,
            'data': args.data,
        }

        if args.priority:
            payload['priority'] = args.priority

        if args.expiration:
            payload['expiration'] = args.expiration

        response = client.invoke('zato.pubsub.topic.publish', payload)

        if response.ok:
            response_data = response.data
            if isinstance(response_data, str):
                response_data = json.loads(response_data)

            # .. the service wraps the result in 'response_body' ..
            response_body = response_data['response_body']
            if isinstance(response_body, str):
                response_body = json.loads(response_body)

            self._print_success('Message published')
            self._print_msg_id(response_body['msg_id'])
        else:
            self._print_error(f'Publish failed: {response.details}')

# ################################################################################################################################
# ################################################################################################################################

class Browse(_PubSubCommand):
    """ Browses messages in a subscription queue.

If --sub-key is omitted, all subscriptions are browsed.

The --state flag filters by delivery state:
  pending   - messages waiting to be delivered (default)
  delivered - messages already delivered to the subscriber
  all       - all messages in the queue regardless of delivery state

Examples:
  zato pubsub browse /path/to/server --state all
  zato pubsub browse /path/to/server --sub-key zato.sub.abc123
  zato pubsub browse /path/to/server --sub-key zato.sub.abc123 --state pending --page 2 --page-size 25
  zato pubsub browse /path/to/server --sub-key zato.sub.abc123 --state delivered
  zato pubsub browse /path/to/server --sub-key zato.sub.abc123 --state all
    """

    opts = [
        {'name':'--sub-key', 'help':'Subscription key (if omitted, browses all subscriptions)'},
        {'name':'--page', 'help':'Page number (default 1)'},
        {'name':'--page-size', 'help':'Messages per page (default 50)'},
        {'name':'--state', 'help':'Delivery state filter: pending (default), delivered, all'},
    ]

    def execute(self, args:'any_') -> 'None':

        # stdlib
        import json

        # colorama
        from colorama import Fore, Style

        client = self._get_client(args)

        # .. if no sub_key given, iterate over all subscriptions ..
        if args.sub_key:
            sub_keys = [args.sub_key]
        else:
            sub_keys = []

        # .. always fetch subscription list to get security names ..
        response = client.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})
        if not response.ok:
            self._print_error(f'Failed to list subscriptions: {response.details}')
            return

        data = response.data
        if isinstance(data, str):
            data = json.loads(data)

        if isinstance(data, list):
            items = data
        else:
            items = data['zato_pubsub_subscription_get_list_response']

        # .. build a sub_key -> sec_name mapping ..
        sec_names:'anydict' = {}
        for item in items:
            sec_names[item['sub_key']] = item['sec_name']

        # .. if no sub_key was given, use all of them ..
        if not sub_keys:
            sub_keys = [item['sub_key'] for item in items]

        for sub_key in sub_keys:

            payload:'anydict' = {
                'sub_key': sub_key,
            }

            if args.page:
                payload['page'] = args.page

            if args.page_size:
                payload['page_size'] = args.page_size

            if args.state:
                payload['state'] = args.state

            response = client.invoke('zato.pubsub.subscription.browse-queue', payload)

            if response.ok:
                data = response.data
                if isinstance(data, str):
                    data = json.loads(data)

                self._print_header(f'Queue: {sub_key} ({sec_names[sub_key]})')
                self._print_count('total', data['total'])
                self._print_field('page', data['page'])
                print()

                for row in data['rows']:
                    self._print_msg_id(row['msg_id'])
                    self._print_field('topic', row['topic_name'])
                    self._print_field('published', row['pub_time_iso'])
                    self._print_field('is_delivered', row['is_delivered'])
                    self._print_field('size', row['data_size'])

                    if preview := row.get('data_preview'):
                        print(f'  {Fore.CYAN}preview:{Style.RESET_ALL} {Fore.WHITE}{preview}{Style.RESET_ALL}')

                    print()
            else:
                self._print_error(f'Browse failed: {response.details}')

# ################################################################################################################################
# ################################################################################################################################

class Get(_PubSubCommand):
    """ Gets a single message with full payload and metadata.

Examples:
  zato pubsub get /path/to/server --msg-id zpsm1234 --topic-name /my/topic --redis-stream-id 1716000000000-0
    """

    opts = [
        {'name':'--msg-id', 'help':'Message ID'},
        {'name':'--topic-name', 'help':'Topic name the message belongs to'},
        {'name':'--redis-stream-id', 'help':'Redis stream entry ID'},
    ]

    def execute(self, args:'any_') -> 'None':

        # stdlib
        import json

        client = self._get_client(args)

        payload = {
            'msg_id': args.msg_id,
            'topic_name': args.topic_name,
            'redis_stream_id': args.redis_stream_id,
        }

        response = client.invoke('zato.pubsub.subscription.get-message-detail', payload)

        if response.ok:
            data = response.data
            if isinstance(data, str):
                data = json.loads(data)

            if 'error' in data:
                self._print_error(data['error'])
                return

            self._print_header('Message detail')
            self._print_msg_id(data['msg_id'])
            self._print_field('topic', data['topic_name'])
            self._print_field('priority', data['priority'])
            self._print_field('expiration', data['expiration'])
            self._print_field('published', data['pub_time_iso'])
            self._print_field('received', data['recv_time_iso'])
            self._print_field('size', data['data_size'])

            if data.get('correl_id'):
                self._print_field('correl_id', data['correl_id'])

            if data.get('in_reply_to'):
                self._print_field('in_reply_to', data['in_reply_to'])

            if data.get('publisher'):
                self._print_field('publisher', data['publisher'])

            if data.get('has_data'):
                print()
                self._print_header('Payload')
                print(data['data'])
        else:
            self._print_error(f'Get failed: {response.details}')

# ################################################################################################################################
# ################################################################################################################################

class Update(_PubSubCommand):
    """ Updates the payload of a message in a queue.

Examples:
  zato pubsub update /path/to/server --msg-id zpsm1234 --topic-name /my/topic --data '{"corrected": true}'
    """

    opts = [
        {'name':'--msg-id', 'help':'Message ID'},
        {'name':'--topic-name', 'help':'Topic name the message belongs to'},
        {'name':'--data', 'help':'New message payload'},
    ]

    def execute(self, args:'any_') -> 'None':

        # stdlib
        import json

        client = self._get_client(args)

        payload = {
            'msg_id': args.msg_id,
            'topic_name': args.topic_name,
            'data': args.data,
        }

        response = client.invoke('zato.pubsub.subscription.update-message', payload)

        if response.ok:
            data = response.data
            if isinstance(data, str):
                data = json.loads(data)

            self._print_success('Message updated')
            self._print_msg_id(data['msg_id'])
        else:
            self._print_error(f'Update failed: {response.details}')

# ################################################################################################################################
# ################################################################################################################################

class Delete(_PubSubCommand):
    """ Deletes a single message from a subscription queue.

Examples:
  zato pubsub delete /path/to/server --msg-id zpsm1234 --topic-name /my/topic --sub-key zato.sub.abc123 --redis-stream-id 1716000000000-0
    """

    opts = [
        {'name':'--msg-id', 'help':'Message ID'},
        {'name':'--topic-name', 'help':'Topic name the message belongs to'},
        {'name':'--sub-key', 'help':'Subscription key'},
        {'name':'--redis-stream-id', 'help':'Redis stream entry ID'},
    ]

    def execute(self, args:'any_') -> 'None':

        # stdlib
        import json

        client = self._get_client(args)

        payload = {
            'msg_id': args.msg_id,
            'topic_name': args.topic_name,
            'sub_key': args.sub_key,
            'redis_stream_id': args.redis_stream_id,
        }

        response = client.invoke('zato.pubsub.subscription.delete-message', payload)

        if response.ok:
            data = response.data
            if isinstance(data, str):
                data = json.loads(data)

            if 'error' in data:
                self._print_error(data['error'])
            else:
                self._print_success('Message deleted')
                self._print_msg_id(data['msg_id'])
        else:
            self._print_error(f'Delete failed: {response.details}')

# ################################################################################################################################
# ################################################################################################################################

class Clear(_PubSubCommand):
    """ Clears all messages from a subscription queue.

Examples:
  zato pubsub clear /path/to/server --sub-key zato.sub.abc123
    """

    opts = [
        {'name':'--sub-key', 'help':'Subscription key'},
    ]

    def execute(self, args:'any_') -> 'None':

        # stdlib
        import json

        client = self._get_client(args)

        payload = {
            'sub_key': args.sub_key,
        }

        response = client.invoke('zato.pubsub.subscription.clear-queue', payload)

        if response.ok:
            data = response.data
            if isinstance(data, str):
                data = json.loads(data)

            self._print_success('Queue cleared')
            self._print_count('cleared', data['cleared_count'])
        else:
            self._print_error(f'Clear failed: {response.details}')

# ################################################################################################################################
# ################################################################################################################################
