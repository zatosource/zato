# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from logging import getLogger

# Zato
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Configure logging format to match Zato format
def setup_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:0 - %(message)s'
    )
    formatter.default_msec_format = '%s.%03d'

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

# ################################################################################################################################
# ################################################################################################################################

_has_rabbitmq_group = os.environ.get('Zato_Has_RabbitMQ_Group')
_has_rabbitmq_group = as_bool(_has_rabbitmq_group)

needs_sudo = not _has_rabbitmq_group

# ################################################################################################################################
# ################################################################################################################################

class RabbitMQCtlHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logger.info(f'Received request with {content_length} bytes')

            request_data = json.loads(post_data.decode('utf-8'))
            command_args = request_data.get('args', '')
            logger.info(f'Command args: {command_args}')

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            temp_file = f'/tmp/rabbitmq_output_{timestamp}.txt'

            prefix = 'sudo -u rabbitmq ' if needs_sudo else ''

            full_command = f'{prefix}/usr/lib/rabbitmq/bin/rabbitmqctl {command_args}'
            logger.info(f'Executing: {full_command}')

            with open(temp_file, 'w') as f:
                result = subprocess.run(
                    full_command,
                    shell=True,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=30
                )

            logger.info(f'Command completed with returncode: {result.returncode}')

            stdout_content = ''
            if os.path.exists(temp_file):
                with open(temp_file, 'r') as f:
                    raw_content = f.read()

                lines = raw_content.strip().split('\n')

                json_start = -1
                json_end = -1

                for i in range(len(lines) - 1, -1, -1):
                    line = lines[i].strip()
                    if line == ']' or line == '}':
                        json_end = i
                        break

                if json_end >= 0:
                    for i in range(json_end, -1, -1):
                        line = lines[i].strip()
                        if line == '[' or line == '{':
                            json_start = i
                            break

                if json_start >= 0 and json_end >= 0:
                    json_lines = lines[json_start:json_end + 1]
                    stdout_content = '\n'.join(json_lines)

            response_data = {
                'returncode': result.returncode,
                'stdout': stdout_content,
                'stderr': ''
            }

            logger.info(f'Response data: {response_data}')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            _ = self.wfile.write(json.dumps(response_data).encode('utf-8'))
            logger.info('Response sent successfully')

        except Exception as e:
            logger.error(f'Error processing request: {e}')
            error_response = {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            _ = self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def log_message(self, format, *args):
        logger.info(f'RabbitMQCtl Server: {format % args}')

# ################################################################################################################################
# ################################################################################################################################

def start_server():
    setup_logging()
    server_address = ('127.0.0.1', 25090)
    httpd = HTTPServer(server_address, RabbitMQCtlHandler)
    logger.info(f'RabbitMQCtl server starting on {server_address[0]}:{server_address[1]}')
    httpd.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    start_server()

# ################################################################################################################################
# ################################################################################################################################
