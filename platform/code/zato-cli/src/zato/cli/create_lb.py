# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, uuid

# Zato
from zato.cli import common_logging_conf_contents, ZatoCommand, ZATO_LB_DIR
from zato.common.defaults import http_plain_server_port

config_template = """{
  "haproxy_command": "haproxy",
  "host": "localhost",
  "port": 20151,
  "keyfile": "./lba-priv-key.pem",
  "certfile": "./lba-cert.pem",
  "ca_certs": "./ca-chain.pem",
  "work_dir": ".",
  "verify_fields": {},
  "log_config": "./logging.conf"
}
"""

zato_config_template = """
# ##############################################################################

global
    log 127.0.0.1:514 local0 debug # ZATO global:log
    stats socket {stats_socket} # ZATO global:stats_socket

# ##############################################################################

defaults
    log global
    option httpclose

    stats uri /zato-lb-stats # ZATO defaults:stats uri

    timeout connect 5000 # ZATO defaults:timeout connect
    timeout client 5000 # ZATO defaults:timeout client
    timeout server 5000 # ZATO defaults:timeout server

    stats enable
    stats realm   Haproxy\ Statistics

    # Note: Although it may seem just the opposite, the password below is
    # written in plain-text. It's not a hash or anything similar.
    stats auth    admin1:{stats_password}

    stats refresh 5s

# ##############################################################################

backend bck_http_plain
    mode http
    balance roundrobin

    server http_plain--QuickstartServerHTTP 127.0.0.1:{http_plain_server_port} check inter 2s rise 2 fall 2 # ZATO backend bck_http_plain:server--QuickstartServerHTTP

# ##############################################################################

frontend front_http_plain

    mode http
    default_backend bck_http_plain

    option httplog # ZATO frontend front_http_plain:option log-http-requests
    bind 127.0.0.1:11223 # ZATO frontend front_http_plain:bind
    maxconn 200 # ZATO frontend front_http_plain:maxconn

    monitor-uri /zato-lb-alive # ZATO frontend front_http_plain:monitor-uri
"""

class CreateLoadBalancer(ZatoCommand):
    command_name = 'create lb-agent'

    needs_empty_dir = True

    def __init__(self, target_dir):
        super(CreateLoadBalancer, self).__init__()
        self.target_dir = target_dir

    description = "Creates a Load Balancer's agent."

    def execute(self, args):

        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(os.path.join(self.target_dir, 'config', 'zdaemon'))
        os.mkdir(os.path.join(self.target_dir, 'logs'))

        log_path = os.path.join(self.target_dir, 'logs', 'lb-agent.log')
        stats_socket = os.path.join(self.target_dir, 'haproxy-stat.sock')

        open(os.path.join(self.target_dir, 'config', 'lb-agent.conf'), 'w').write(config_template)
        open(os.path.join(self.target_dir, 'config', 'logging.conf'), 'w').write((common_logging_conf_contents.format(log_path=log_path)))
        open(os.path.join(self.target_dir, ZATO_LB_DIR), 'w').close()

        zato_config = zato_config_template.format(stats_socket=stats_socket,
                stats_password=uuid.uuid4().hex,
                http_plain_server_port=http_plain_server_port)
        open(os.path.join(self.target_dir, 'config', 'zato.config'), 'w').write(zato_config)

        msg = """\nSuccessfully created a Load Balancer's agent.
You can now go to {path} and start it with the 'zato start lb-agent' command.
""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))

        print(msg)

def main(target_dir):
    CreateLoadBalancer(target_dir).run()

if __name__ == "__main__":
    main(".")
