# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import time

# gevent
from gevent.wsgi import WSGIServer # type: ignore

# Zato
from zato.common.monitoring.api import create_context, get_metrics_data, incr_global, push_global

# ################################################################################################################################
# ################################################################################################################################

class PrometheusTestServer:
    """ Gevent-based test server for validating metrics framework.
    """

    def __init__(self, host:'str' = '0.0.0.0', port:'int' = 8080) -> 'None':
        self.host = host
        self.port = port
        self.server = None

    def wsgi_app(self, environ, start_response):
        """ WSGI application handler.
        """
        path = environ.get('PATH_INFO', '')

        if path == '/metrics':
            try:
                metrics_data = get_metrics_data()
                start_response('200 OK', [
                    ('Content-Type', 'text/plain; version=0.0.4; charset=utf-8'),
                    ('Content-Length', str(len(metrics_data)))
                ])
                return [metrics_data.encode('utf-8')]
            except Exception as e:
                error_msg = f'Error generating metrics: {e}'
                start_response('500 Internal Server Error', [
                    ('Content-Type', 'text/plain'),
                    ('Content-Length', str(len(error_msg)))
                ])
                return [error_msg.encode('utf-8')]

        elif path == '/':
            html = """<!DOCTYPE html>
<html><head><title>Zato Monitoring Test Server</title></head>
<body>
<h1>Zato Monitoring Test Server</h1>
<p><a href="/metrics">Metrics endpoint</a></p>
<p><a href="/demo">Demo data</a></p>
</body></html>"""
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(html)))
            ])
            return [html.encode('utf-8')]

        elif path == '/demo':
            self._generate_demo_data()
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'Demo data generated. Check /metrics']

        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']

    def _generate_demo_data(self) -> 'None':
        """ Generate sample metrics for testing.
        """
        # Sample aircraft handling process
        aircraft_ctx = create_context('AircraftHandling', 'ABC123')
        aircraft_ctx.push('bags_loaded', 142)
        aircraft_ctx.push('fuel_liters', 48500)
        aircraft_ctx.push('turnaround_minutes', 35)
        aircraft_ctx.push_timestamp('gate_assigned')

        # Sample applicant processing
        applicant_ctx = create_context('ApplicantProcessing', 'APP456')
        applicant_ctx.push('courses_assigned', 3)
        applicant_ctx.push('courses_completed', 1)
        applicant_ctx.timer_start('processing_time')
        time.sleep(0.001)  # Simulate brief processing
        applicant_ctx.timer_stop('processing_time')

        # Global counters
        incr_global('total_requests')
        incr_global('total_requests')
        push_global('system_load', 0.65)

    def start(self) -> 'None':
        """ Start the test server.
        """
        print(f'Starting Zato Monitoring Test Server on {self.host}:{self.port}')
        print(f'Metrics endpoint: http://{self.host}:{self.port}/metrics')
        print(f'Demo data: http://{self.host}:{self.port}/demo')

        self.server = WSGIServer((self.host, self.port), self.wsgi_app)
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.server.stop()

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Main entry point.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Zato Monitoring Test Server')
    _ = parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    _ = parser.add_argument('--port', type=int, default=8080, help='Port to bind to')

    args = parser.parse_args()

    server = PrometheusTestServer(args.host, args.port)
    server.start()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
