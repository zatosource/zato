# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# PyYAML
import yaml

# Zato
from zato.common.crypto.api import CryptoManager

# Live environment
from live_containers.ready import wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The service the suite deploys to hold locks and read subscription rows
    Runtime_Service      = 'ha.pubsub.subscription.runtime'
    Runtime_Service_File = 'ha_pubsub_subscription_runtime.py'

    # The markers the server writes for each pickup import
    Marker_Started   = 'Invoking command'
    Marker_Import    = '--import'
    Marker_Completed = 'Enmasse stderr'

    Log_Path = os.path.join('logs', 'server.log')

    # How long a pickup import may take, in seconds
    Import_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

class Names:
    """ The object names of one live environment of the suite.
    """

    def __init__(self) -> 'None':
        suffix = CryptoManager.generate_hex_string(8)

        self.security_pull = f'ha.sub.sec.pull.{suffix}'
        self.security_second = f'ha.sub.sec.second.{suffix}'
        self.topic_pull = f'ha.sub.topic.pull.{suffix}'
        self.topic_second = f'ha.sub.topic.second.{suffix}'
        self.password = 'password.' + CryptoManager.generate_hex_string()

# ################################################################################################################################

    def placeholders(self) -> 'strstrdict':
        """ Returns the placeholders of the enmasse template.
        """
        out = {
            'security_pull': self.security_pull,
            'security_second': self.security_second,
            'topic_pull': self.topic_pull,
            'topic_second': self.topic_second,
            'password': self.password,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

class Pickup:
    """ Places enmasse files in the pickup directory and waits for each import to complete.
    """

    def __init__(self, environment:'ZatoEnvironment') -> 'None':
        self.environment = environment
        self.counter = 0
        self.log_path = os.path.join(environment.server_directory, ModuleCtx.Log_Path)

# ################################################################################################################################

    def _read_log(self) -> 'str':
        if not os.path.isfile(self.log_path):
            return ''

        with open(self.log_path) as log_file:
            out = log_file.read()

        return out

# ################################################################################################################################

    def _count_completed(self, text:'str') -> 'int':
        completed = 0

        for line in text.splitlines():
            if ModuleCtx.Marker_Completed in line:
                completed += 1

        return completed

# ################################################################################################################################

    def apply(self, name:'str', definitions:'str') -> 'None':
        """ Writes an enmasse file into the pickup directory and waits for the import to complete.
        """
        before = self._count_completed(self._read_log())
        self.counter += 1

        file_name = f'enmasse-{self.counter:04d}-{name}.yaml'
        path = os.path.join(self.environment.pickup_directory, file_name)

        with open(path, 'w') as enmasse_file:
            _ = enmasse_file.write(definitions)

        def _completed() -> 'bool':
            out = self._count_completed(self._read_log()) > before
            return out

        wait_until(_completed, f'pickup import {file_name}', timeout=ModuleCtx.Import_Timeout)

# ################################################################################################################################
# ################################################################################################################################

class Runtime:
    """ Invokes the runtime service of the suite.
    """

    def __init__(self, client:'AdminClient') -> 'None':
        self.client = client

# ################################################################################################################################

    def invoke(self, request:'anydict') -> 'anydict':
        response = self.client.invoke(ModuleCtx.Runtime_Service, request)
        return response

# ################################################################################################################################

    def hold_locks(self, topic_name:'str', hold_seconds:'float') -> 'None':
        """ Holds the write lock of the pub/sub database for the given time.
        """
        _ = self.invoke({
            'action': 'hold_locks',
            'topic_name': topic_name,
            'hold_seconds': hold_seconds,
            'row_count': 1,
        })

# ################################################################################################################################

    def governed_pairs(self) -> 'list':
        """ Returns the governed subscriber and topic pairs of the pub/sub database.
        """
        response = self.invoke({'action': 'governed_pairs'})
        out = response['pairs']
        return out

# ################################################################################################################################

    def statuses(self) -> 'list':
        """ Returns the statuses of the subscription list.
        """
        response = self.invoke({'action': 'statuses'})
        out = response['statuses']
        return out

# ################################################################################################################################

    def kill_worker(self) -> 'None':
        """ Sends SIGKILL to the worker process of the server.
        """
        _ = self.invoke({'action': 'kill_worker'})

# ################################################################################################################################
# ################################################################################################################################

def render_template(template_path:'str', placeholders:'strstrdict') -> 'str':
    """ Returns the enmasse YAML with the placeholders substituted.
    """
    with open(template_path) as template_file:
        template = template_file.read()

    out = template.format(**placeholders)
    return out

# ################################################################################################################################

def yaml_add_second_topic(names:'Names') -> 'str':
    """ Returns an enmasse file that adds the second topic to the pull subscription.
    """
    definition = {
        'pubsub_subscription': [{
            'security': names.security_pull,
            'delivery_type': 'pull',
            'topic_list': [names.topic_pull, names.topic_second],
        }],
    }
    out = yaml.dump(definition)
    return out

# ################################################################################################################################

def yaml_remove_pull_topic(names:'Names') -> 'str':
    """ Returns an enmasse file that removes the pull topic from the pull subscription.
    """
    definition = {
        'pubsub_subscription': [{
            'security': names.security_pull,
            'delivery_type': 'pull',
            'topic_list': [names.topic_second],
        }],
    }
    out = yaml.dump(definition)
    return out

# ################################################################################################################################

def wait_for_no_unconfirmed(runtime:'Runtime', timeout:'float'=60.0) -> 'None':
    """ Waits until the subscription list has no unconfirmed pairs.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        statuses = runtime.statuses()
        unconfirmed = False

        for _sub_key, _topic, status in statuses:
            if status != 'confirmed':
                unconfirmed = True
                break

        if not unconfirmed:
            return

        time.sleep(0.5)

    raise Exception('The subscription list still has unconfirmed pairs')

# ################################################################################################################################
# ################################################################################################################################
