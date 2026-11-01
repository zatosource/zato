# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Toxiproxy as a test container on the network of the host, with one proxy per link of item 15.6 - the link
# from the server to PostgreSQL and the link from the server to each push subscriber.

# stdlib
import os
import socket
from time import monotonic

# gevent
from gevent import sleep

# requests
import requests

# Zato
from container import run_command

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_image = 'ghcr.io/shopify/toxiproxy:2.12.0'
_host = '127.0.0.1'
Toxiproxy_Host = _host

# How long the API may take to come up and how long one call to it may take, in seconds.
_start_timeout = 60
_api_timeout = 30
_start_poll_seconds = 0.2

# The directions of a link - what the client sends and what it receives.
Stream_Upstream   = 'upstream'
Stream_Downstream = 'downstream'

Both_Streams = [Stream_Upstream, Stream_Downstream]

# The counter of the bytes that a proxy received, by direction, in the metrics of Toxiproxy.
_received_bytes_metric = 'toxiproxy_proxy_received_bytes_total'

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((_host, 0))
        address = probe.getsockname()

    out = address[1]
    return out

# ################################################################################################################################
# ################################################################################################################################

class Toxiproxy:
    """ One container of Toxiproxy, its proxies and their toxics.
    """

    def __init__(self, label:'str') -> 'None':
        pid = os.getpid()

        self.name = f'zato-pubsub-test-toxiproxy-{label}-{pid}'
        self.api_port = find_free_port()
        self.address = f'http://{_host}:{self.api_port}'

# ################################################################################################################################

    def _call(self, method:'str', path:'str', body:'anydict | None'=None) -> 'requests.Response':
        url = self.address + path

        out = requests.request(method, url, json=body, timeout=_api_timeout)
        out.raise_for_status()

        return out

# ################################################################################################################################

    def start(self) -> 'None':
        command:'strlist' = [
            'docker', 'run', '-d', '--rm', '--name', self.name, '--network', 'host',
            _image, f'-host={_host}', f'-port={self.api_port}', '-proxy-metrics',
        ]
        _ = run_command(command)

        # The container is ready once its API responds.
        deadline = monotonic() + _start_timeout

        while True:
            try:
                _ = self._call('GET', '/version')
                break
            except requests.ConnectionError:
                assert monotonic() < deadline, f'Toxiproxy {self.name} not up after {_start_timeout}s'
                sleep(_start_poll_seconds)

# ################################################################################################################################

    def stop(self) -> 'None':
        _ = run_command(['docker', 'rm', '-f', self.name])

# ################################################################################################################################

    def add_proxy(self, name:'str', upstream_port:'int', upstream_host:'str'=_host) -> 'int':
        """ Creates a proxy to a port of the host, or of another address, and returns the port it listens on.
        """
        out = find_free_port()

        body = {
            'name': name,
            'listen': f'{_host}:{out}',
            'upstream': f'{upstream_host}:{upstream_port}',
            'enabled': True,
        }
        _ = self._call('POST', '/proxies', body)

        return out

# ################################################################################################################################

    def add_toxic(self, proxy:'str', toxic_type:'str', attributes:'anydict', stream:'str', toxicity:'float'=1.0) -> 'None':
        body = {
            'name': f'{toxic_type}-{stream}',
            'type': toxic_type,
            'stream': stream,
            'toxicity': toxicity,
            'attributes': attributes,
        }
        _ = self._call('POST', f'/proxies/{proxy}/toxics', body)

# ################################################################################################################################

    def remove_toxics(self, proxy:'str') -> 'None':
        response = self._call('GET', f'/proxies/{proxy}/toxics')
        toxics = response.json()

        for toxic in toxics:
            toxic_name = toxic['name']
            _ = self._call('DELETE', f'/proxies/{proxy}/toxics/{toxic_name}')

# ################################################################################################################################

    def read_received_bytes(self, proxy:'str') -> 'int':
        """ How many bytes the proxy received in both directions since it was created.
        """
        response = self._call('GET', '/metrics')
        proxy_label = f'proxy="{proxy}"'

        out = 0

        for line in response.text.splitlines():
            if line.startswith(_received_bytes_metric):
                if proxy_label in line:
                    _, value = line.rsplit(' ', 1)
                    out += int(float(value))

        return out

# ################################################################################################################################
# ################################################################################################################################
