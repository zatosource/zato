# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import shutil
import subprocess
import tempfile
import time
from logging import getLogger

# kombu
from kombu import Connection

# Zato
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.util.api import new_cid
from zato.common.util.proc import start_process

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# RabbitMQ's default account, which is always allowed to connect over localhost
_default_username = 'guest'
_default_password = 'guest'

# How long to wait for the broker to accept AMQP connections after it was started
_startup_timeout = 60

# How long to wait for the AMQP port to stop accepting connections after shutdown
_shutdown_timeout = 30

# How often to poll for broker readiness
_poll_interval = 0.5

# What the enabled-plugins file contains - no plugins at all, for faster startup and no extra ports
_no_plugins = '[].'

# Debian and Ubuntu install the real rabbitmqctl here - the /usr/sbin wrapper on PATH
# refuses to run for regular users, printing "Only root or rabbitmq should run rabbitmqctl"
_debian_rabbitmqctl = '/usr/lib/rabbitmq/bin/rabbitmqctl'

# Default timeout for draining queues in tests
_drain_timeout = 5.0

# ################################################################################################################################
# ################################################################################################################################

class RabbitMQProcess:
    """ A private RabbitMQ node for tests - non-root, random ports, tmp directories,
    removed on teardown. Assumes rabbitmq-server is on PATH.
    """

    def __init__(self) -> 'None':

        # Everything the node needs lives under this directory
        self.base_directory = tempfile.mkdtemp(prefix='zato_test_rabbitmq_')

        # Random ports so parallel brokers never clash
        self.amqp_port = find_free_port()
        self.dist_port = find_free_port()

        # A unique node name so parallel brokers never clash either. No explicit host part,
        # both rabbitmq-server and rabbitmqctl then resolve the local hostname the same way.
        cid = new_cid()
        self.nodename = f'zato-test-{cid}'

        # The URL AMQP clients connect with
        self.amqp_url = f'amqp://{_default_username}:{_default_password}@127.0.0.1:{self.amqp_port}//'

        # Where the node writes its pid, used as the last-resort kill switch
        self.pid_file = os.path.join(self.base_directory, 'rabbitmq.pid')

        # The enabled-plugins file needs to exist before the node starts
        self.enabled_plugins_file = os.path.join(self.base_directory, 'enabled_plugins')

        with open(self.enabled_plugins_file, 'w') as plugins_file:
            _ = plugins_file.write(_no_plugins)

        self.is_running = False

        # Make sure everything is stopped and removed even if the caller forgets
        _ = atexit.register(self.stop)

# ################################################################################################################################

    def get_environment(self) -> 'strstrdict':
        """ Returns the environment variables the node and rabbitmqctl need.
        HOME points at the base directory so the Erlang cookie lands there.
        """
        return {
            'RABBITMQ_NODENAME': self.nodename,
            'RABBITMQ_NODE_IP_ADDRESS': '127.0.0.1',
            'RABBITMQ_NODE_PORT': str(self.amqp_port),
            'RABBITMQ_DIST_PORT': str(self.dist_port),
            'RABBITMQ_MNESIA_BASE': os.path.join(self.base_directory, 'mnesia'),
            'RABBITMQ_LOG_BASE': os.path.join(self.base_directory, 'logs'),
            'RABBITMQ_PID_FILE': self.pid_file,
            'RABBITMQ_ENABLED_PLUGINS_FILE': self.enabled_plugins_file,
            'HOME': self.base_directory,
        }

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the node in background and waits until it accepts AMQP connections.
        """
        start_time = time.monotonic()

        logger.info('Starting RabbitMQ node `%s` on port %d in %s', self.nodename, self.amqp_port, self.base_directory)

        _ = start_process(
            component_name='test-rabbitmq',
            executable='rabbitmq-server',
            run_in_fg=False,
            cli_options=None,
            env_vars=self.get_environment(),
        )

        self.is_running = True

        # Poll the AMQP port until the broker accepts connections
        deadline = start_time + _startup_timeout

        while time.monotonic() < deadline:
            try:
                with Connection(self.amqp_url) as connection:
                    _ = connection.ensure_connection(max_retries=1, timeout=1)
                logger.info('RabbitMQ node `%s` ready after %.1fs', self.nodename, time.monotonic() - start_time)
                return
            except Exception:
                time.sleep(_poll_interval)

        raise RuntimeError(f'RabbitMQ node `{self.nodename}` did not start within {_startup_timeout}s')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Shuts the node down and removes its base directory. Registered with atexit
        so calling it multiple times must be safe.
        """
        if self.is_running:

            logger.info('Stopping RabbitMQ node `%s`', self.nodename)

            # rabbitmqctl needs the same environment, particularly HOME for the Erlang cookie
            environment = dict(os.environ)
            environment.update(self.get_environment())

            # Prefer the real binary over the wrapper that rejects non-root users
            if os.path.exists(_debian_rabbitmqctl):
                rabbitmqctl = _debian_rabbitmqctl
            else:
                rabbitmqctl = 'rabbitmqctl'

            result = subprocess.run(
                [rabbitmqctl, '-n', self.nodename, 'shutdown'],
                env=environment,
                capture_output=True,
                timeout=_shutdown_timeout,
            )

            if result.returncode != 0:
                logger.warning('rabbitmqctl shutdown failed for `%s` - %s', self.nodename, result.stderr.decode('utf8'))

            # Wait until the AMQP port stops accepting connections
            deadline = time.monotonic() + _shutdown_timeout
            is_port_closed = False

            while time.monotonic() < deadline:
                try:
                    with Connection(self.amqp_url) as connection:
                        _ = connection.ensure_connection(max_retries=1, timeout=1)
                    time.sleep(_poll_interval)
                except Exception:
                    is_port_closed = True
                    break

            # If rabbitmqctl could not stop the node, kill the beam process through its pid file
            if not is_port_closed:
                self._kill_via_pid_file()

            self.is_running = False

        # Remove the base directory with mnesia, logs, pid and the cookie
        if os.path.exists(self.base_directory):
            shutil.rmtree(self.base_directory, ignore_errors=True)
            logger.info('Removed RabbitMQ base directory %s', self.base_directory)

# ################################################################################################################################

    def _kill_via_pid_file(self) -> 'None':
        """ The last resort when rabbitmqctl cannot reach the node - kill the beam process directly.
        """
        import signal

        if not os.path.exists(self.pid_file):
            logger.warning('No pid file at %s, cannot kill node `%s`', self.pid_file, self.nodename)
            return

        with open(self.pid_file, 'r') as pid_source:
            pid = int(pid_source.read().strip())

        logger.warning('Killing RabbitMQ node `%s` via pid %d', self.nodename, pid)

        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            # Already gone, which is what was needed anyway
            pass

# ################################################################################################################################
# ################################################################################################################################

def declare_and_bind(amqp_url:'str', exchange:'str', queue:'str', routing_key:'str') -> 'None':
    """ Declares a direct exchange, a queue and a binding between them.
    """
    from kombu import Exchange, Queue

    with Connection(amqp_url) as connection:
        channel = connection.channel()

        exchange_declaration = Exchange(exchange, type='direct', durable=True)
        queue_declaration = Queue(queue, exchange=exchange_declaration, routing_key=routing_key, durable=True)

        # Binding the queue declares the exchange, the queue and the binding itself
        bound_queue = queue_declaration(channel)
        bound_queue.declare()

# ################################################################################################################################

def publish_to_exchange(amqp_url:'str', exchange:'str', routing_key:'str', body:'any_') -> 'None':
    """ Publishes a message to an exchange the way an external AMQP producer would.
    """
    with Connection(amqp_url) as connection:
        producer = connection.Producer()
        producer.publish(body, exchange=exchange, routing_key=routing_key)

# ################################################################################################################################

def drain_queue(amqp_url:'str', queue:'str', timeout:'float'=_drain_timeout) -> 'anylist':
    """ Collects all message bodies from a queue within the timeout, acking each one.
    Waits for the full timeout so tests can assert that nothing extra arrives.
    """
    out = []

    deadline = time.monotonic() + timeout

    with Connection(amqp_url) as connection:
        channel = connection.channel()

        while time.monotonic() < deadline:

            message = channel.basic_get(queue=queue, no_ack=False)

            # An empty queue means we wait for more messages until the deadline
            if message is None:
                time.sleep(0.1)
                continue

            body = message.body

            # py-amqp may hand the body over as raw buffers
            if isinstance(body, memoryview):
                body = body.tobytes()

            if isinstance(body, bytes):
                body = body.decode('utf8')

            out.append(body)
            channel.basic_ack(message.delivery_tag)

    return out

# ################################################################################################################################

def get_queue_depth(amqp_url:'str', queue:'str') -> 'int':
    """ Returns how many messages are waiting in a queue, using a passive declare.
    """
    with Connection(amqp_url) as connection:
        channel = connection.channel()
        declaration = channel.queue_declare(queue=queue, passive=True)

        out = declaration.message_count
        return out

# ################################################################################################################################
# ################################################################################################################################
