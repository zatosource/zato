# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# Configure logging format to match Zato format
def setup_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:0 - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S,%f'
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

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

            full_command = f'sudo -u rabbitmq /usr/lib/rabbitmq/bin/rabbitmqctl {command_args}'
            logger.info(f'Executing: {full_command}')

            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            logger.info(f'Command completed with returncode: {result.returncode}')
            if result.stderr:
                logger.warning(f'Command stderr: {result.stderr}')

            response_data = {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
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
