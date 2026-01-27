# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from unittest import TestCase, main

# Zato
from zato.openapi.generator.io_scanner import IOScanner

# ################################################################################################################################
# ################################################################################################################################

class TestSelfContainedServices(TestCase):

    def test_two_services_extracted(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_self_contained_services.py')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)

            services = result['services']

            self.assertEqual(len(services), 2)

            service_names = [s['name'] for s in services]
            self.assertIn('test.route.get', service_names)
            self.assertIn('test.route.create', service_names)

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_all_models_extracted(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_self_contained_services.py')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)

            models = result['models']

            expected_models = [
                'Runway',
                'Terminal',
                'Airport',
                'Airline',
                'FlightLeg',
                'FlightRoute',
                'GetRouteRequest',
                'GetRouteResponse',
                'CreateRouteRequest',
                'CreateRouteResponse',
            ]

            for model_name in expected_models:
                self.assertIn(model_name, models, f'Model {model_name} not found')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_nested_model_structure(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_self_contained_services.py')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)

            models = result['models']

            route_model = models.get('FlightRoute', {})
            route_fields = route_model.get('fields', {})

            self.assertIn('airline', route_fields)
            self.assertIn('legs', route_fields)

            airline_field = route_fields.get('airline', {})
            self.assertEqual(airline_field.get('type'), 'Airline')

            legs_field = route_fields.get('legs', {})
            legs_type = legs_field.get('type')
            self.assertEqual(legs_type.get('container'), 'list')
            self.assertEqual(legs_type.get('element_type'), 'FlightLeg')

            airline_model = models.get('Airline', {})
            airline_fields = airline_model.get('fields', {})

            hub_field = airline_fields.get('hub', {})
            self.assertEqual(hub_field.get('type'), 'Airport')

            airport_model = models.get('Airport', {})
            airport_fields = airport_model.get('fields', {})

            runways_field = airport_fields.get('runways', {})
            runways_type = runways_field.get('type')
            self.assertEqual(runways_type.get('container'), 'list')
            self.assertEqual(runways_type.get('element_type'), 'Runway')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_service_io_types(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_self_contained_services.py')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)

            services = result['services']

            get_service = next(s for s in services if s['name'] == 'test.route.get')
            create_service = next(s for s in services if s['name'] == 'test.route.create')

            self.assertEqual(get_service['input']['type'], 'model')
            self.assertEqual(get_service['input']['model_name'], 'GetRouteRequest')
            self.assertEqual(get_service['output']['type'], 'model')
            self.assertEqual(get_service['output']['model_name'], 'GetRouteResponse')

            self.assertEqual(create_service['input']['type'], 'model')
            self.assertEqual(create_service['input']['model_name'], 'CreateRouteRequest')
            self.assertEqual(create_service['output']['type'], 'model')
            self.assertEqual(create_service['output']['model_name'], 'CreateRouteResponse')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
