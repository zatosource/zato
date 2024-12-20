# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os, uuid

# Zato
from zato.cli import is_arg_given, ZatoCommand
from zato.common.defaults import http_plain_server_port
from zato.common.util.open_ import open_w

config_template = """{{
  "haproxy_command": "haproxy",
  "host": "localhost",
  "port": 20151,
  "is_tls_enabled": false,
  "keyfile": "./zato-lba-priv-key.pem",
  "certfile": "./zato-lba-cert.pem",
  "ca_certs": "./zato-lba-ca-certs.pem",
  "work_dir": "../",
  "verify_fields": {{}},
  "log_config": "./logging.conf",
  "pid_file": "zato-lb-agent.pid"
}}
"""

zato_config_template = r"""
# ##############################################################################

global
    log 127.0.0.1:514 local0 debug # ZATO global:log
    stats socket {stats_socket} # ZATO global:stats_socket

# ##############################################################################

defaults
    log global
    option httpclose

    stats uri /zato-lb-stats # ZATO defaults:stats uri

    timeout connect 15000 # ZATO defaults:timeout connect
    timeout client 15000 # ZATO defaults:timeout client
    timeout server 15000 # ZATO defaults:timeout server

    errorfile 503 {http_503_path}

    stats enable
    stats realm   Haproxy\ Statistics

    # Note: The password below is a UUID4 written in plain-text.
    stats auth    admin1:{stats_password}

    stats refresh 5s

# ##############################################################################

backend bck_http_plain
    mode http
    balance roundrobin

# ZATO begin backend bck_http_plain

{default_backend}

# ZATO end backend bck_http_plain

# ##############################################################################

frontend front_http_plain

    mode http
    default_backend bck_http_plain

    option forwardfor
    option httplog # ZATO frontend front_http_plain:option log-http-requests
    bind 0.0.0.0:11223 # ZATO frontend front_http_plain:bind
    maxconn 200 # ZATO frontend front_http_plain:maxconn

    monitor-uri /zato-lb-alive # ZATO frontend front_http_plain:monitor-uri
""" # noqa

default_backend = """
    server http_plain--server1 127.0.0.1:{server01_port} check inter 2s rise 2 fall 2 # ZATO backend bck_http_plain:server--server1
"""

http_503 = """HTTP/1.0 503 Service Unavailable
Cache-Control: no-cache
Connection: close
Content-Type: application/json

{"zato_env":
  {"details": "No server is available to handle the request",
  "result": "ZATO_ERROR",
  "cid": "K012345678901234567890123456"}
}
"""

class Create(ZatoCommand):
    """ Creates a new Zato load-balancer
    """
    opts = []
    opts.append({'name':'--pub-key-path', 'help':"Path to the load-balancer agent's public key in PEM"})
    opts.append({'name':'--priv-key-path', 'help':"Path to the load-balancer agent's private key in PEM"})
    opts.append({'name':'--cert-path', 'help':"Path to the load-balancer agent's certificate in PEM"})
    opts.append({'name':'--ca-certs-path', 'help':"Path to the a PEM list of certificates the load-balancer's agent will trust"})

    needs_empty_dir = True

    def __init__(self, args):
        super(Create, self).__init__(args)
        self.target_dir = os.path.abspath(args.path) # noqa

    def execute(self, args, use_default_backend=False, server02_port=None, show_output=True):

        # Zato
        from zato.common.util.logging_ import get_logging_conf_contents

        os.mkdir(os.path.join(self.target_dir, 'config')) # noqa
        os.mkdir(os.path.join(self.target_dir, 'logs')) # noqa

        repo_dir = os.path.join(self.target_dir, 'config', 'repo') # noqa
        os.mkdir(repo_dir) # noqa

        log_path = os.path.abspath(os.path.join(repo_dir, '..', '..', 'logs', 'lb-agent.log')) # noqa
        stats_socket = os.path.join(self.target_dir, 'haproxy-stat.sock') # noqa

        is_tls_enabled = is_arg_given(args, 'priv_key_path')
        config = config_template.format(**{
            'is_tls_enabled': is_tls_enabled,
        })

        logging_conf_contents = get_logging_conf_contents()

        open_w(os.path.join(repo_dir, 'lb-agent.conf')).write(config) # noqa
        open_w(os.path.join(repo_dir, 'logging.conf')).write(logging_conf_contents) # noqa

        if use_default_backend:
            backend = default_backend.format(server01_port=http_plain_server_port, server02_port=server02_port)
        else:
            backend = '\n# ZATO default_backend_empty'

        zato_config = zato_config_template.format(
            stats_socket=stats_socket,
            stats_password=uuid.uuid4().hex,
            default_backend=backend,
            http_503_path=os.path.join(repo_dir, '503.http')) # noqa

        open_w(os.path.join(repo_dir, 'zato.config')).write(zato_config) # noqa
        open_w(os.path.join(repo_dir, '503.http')).write(http_503) # noqa

        self.copy_lb_crypto(repo_dir, args)

        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.LOAD_BALANCER.code)

        if show_output:
            if self.verbose:
                msg = "Successfully created a load-balancer's agent in {}".format(self.target_dir)
                self.logger.debug(msg)
            else:
                self.logger.info('OK')
