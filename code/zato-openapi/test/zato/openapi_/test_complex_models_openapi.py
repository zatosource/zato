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

class TestComplexNestedModels(TestCase):

    def test_deeply_nested_models_extraction(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_nested_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)

            services = result['services']
            models = result['models']

            self.assertEqual(len(services), 1)

            service = services[0]
            service_name = service['name']
            service_input = service['input']
            service_output = service['output']

            self.assertEqual(service_name, 'test.complex.flight.get-details')
            self.assertEqual(service_input['type'], 'model')
            self.assertEqual(service_input['model_name'], 'GetFlightRequest')
            self.assertEqual(service_output['type'], 'model')
            self.assertEqual(service_output['model_name'], 'GetFlightResponse')

            expected_models = [
                'GetFlightRequest',
                'GetFlightResponse',
                'Flight',
                'Aircraft',
                'AircraftType',
                'AircraftManufacturer',
                'Gate',
                'Terminal',
                'Airport',
                'City',
                'Land',
                'Continent',
            ]

            for model_name in expected_models:
                self.assertIn(model_name, models, f'Model {model_name} not found')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_nested_model_fields_correct(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_nested_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)
            models = result['models']

            flight_model = models.get('Flight', {})
            flight_fields = flight_model.get('fields', {})

            self.assertIn('flight_number', flight_fields)
            self.assertIn('aircraft', flight_fields)
            self.assertIn('departure_gate', flight_fields)
            self.assertIn('arrival_gate', flight_fields)

            aircraft_field = flight_fields.get('aircraft', {})
            aircraft_type = aircraft_field.get('type')
            self.assertEqual(aircraft_type, 'Aircraft')

            gate_model = models.get('Gate', {})
            gate_fields = gate_model.get('fields', {})

            self.assertIn('gate_number', gate_fields)
            self.assertIn('terminal', gate_fields)

            terminal_field = gate_fields.get('terminal', {})
            terminal_type = terminal_field.get('type')
            self.assertEqual(terminal_type, 'Terminal')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################
# ################################################################################################################################

class TestComplexSharedModels(TestCase):

    def test_multiple_services_sharing_models(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_shared_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)

            services = result['services']
            models = result['models']

            self.assertEqual(len(services), 3)

            service_names = [s['name'] for s in services]
            self.assertIn('test.complex.checkin.passenger', service_names)
            self.assertIn('test.complex.checkin.get-boarding-pass', service_names)
            self.assertIn('test.complex.checkin.get-flight-passengers', service_names)

            expected_models = [
                'Passenger',
                'Airline',
                'BaggageTag',
                'Baggage',
                'Seat',
                'BoardingPass',
                'CheckInRecord',
                'CheckInPassengerRequest',
                'CheckInPassengerResponse',
                'GetBoardingPassRequest',
                'GetBoardingPassResponse',
                'GetFlightPassengersRequest',
                'GetFlightPassengersResponse',
            ]

            for model_name in expected_models:
                self.assertIn(model_name, models, f'Model {model_name} not found')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_list_of_nested_models(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_shared_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)
            models = result['models']

            checkin_model = models.get('CheckInRecord', {})
            checkin_fields = checkin_model.get('fields', {})

            self.assertIn('baggage_list', checkin_fields)

            baggage_field = checkin_fields.get('baggage_list', {})
            baggage_type = baggage_field.get('type')

            self.assertIsInstance(baggage_type, dict)
            self.assertEqual(baggage_type.get('container'), 'list')
            self.assertEqual(baggage_type.get('element_type'), 'Baggage')

            self.assertIn('passenger', checkin_fields)
            passenger_field = checkin_fields.get('passenger', {})
            passenger_type = passenger_field.get('type')
            self.assertEqual(passenger_type, 'Passenger')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_passenger_model_reused_across_fields(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_shared_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)
            models = result['models']

            checkin_model = models.get('CheckInRecord', {})
            checkin_fields = checkin_model.get('fields', {})

            baggage_model = models.get('Baggage', {})
            baggage_fields = baggage_model.get('fields', {})

            boarding_model = models.get('BoardingPass', {})
            boarding_fields = boarding_model.get('fields', {})

            self.assertEqual(checkin_fields.get('passenger', {}).get('type'), 'Passenger')
            self.assertEqual(baggage_fields.get('passenger', {}).get('type'), 'Passenger')
            self.assertEqual(boarding_fields.get('passenger', {}).get('type'), 'Passenger')

            self.assertIn('Passenger', models)

            passenger_model = models.get('Passenger', {})
            passenger_fields = passenger_model.get('fields', {})

            self.assertIn('first_name', passenger_fields)
            self.assertIn('passport_number', passenger_fields)

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################
# ################################################################################################################################

class TestComplexScheduleModels(TestCase):

    def test_schedule_deeply_nested_with_lists(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_catalog_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)

            services = result['services']
            models = result['models']

            self.assertEqual(len(services), 2)

            expected_models = [
                'Coordinates',
                'Runway',
                'WeatherCondition',
                'METAR',
                'AirportWeather',
                'CrewMember',
                'CrewAssignment',
                'FlightCrew',
                'FuelLoad',
                'RouteWaypoint',
                'FlightPlan',
                'FlightStatus',
                'ScheduledFlight',
                'FlightSearchFilters',
                'SortOption',
                'Pagination',
                'SearchFlightsRequest',
                'SearchFlightsResponse',
                'GetFlightPlanRequest',
                'GetFlightPlanResponse',
            ]

            for model_name in expected_models:
                self.assertIn(model_name, models, f'Model {model_name} not found')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_scheduled_flight_complex_structure(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_catalog_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)
            models = result['models']

            flight_model = models.get('ScheduledFlight', {})
            flight_fields = flight_model.get('fields', {})

            self.assertIn('flight_id', flight_fields)
            self.assertIn('flight_number', flight_fields)
            self.assertIn('flight_plan', flight_fields)
            self.assertIn('crew', flight_fields)
            self.assertIn('departure_weather', flight_fields)
            self.assertIn('arrival_weather', flight_fields)
            self.assertIn('status', flight_fields)

            plan_field = flight_fields.get('flight_plan', {})
            self.assertEqual(plan_field.get('type'), 'FlightPlan')

            crew_field = flight_fields.get('crew', {})
            self.assertEqual(crew_field.get('type'), 'FlightCrew')

            weather_field = flight_fields.get('departure_weather', {})
            self.assertEqual(weather_field.get('type'), 'AirportWeather')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################

    def test_airport_weather_nested_lists(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            test_file = os.path.join(services_dir, 'test_complex_catalog_models.py')

            if not os.path.exists(test_file):
                self.skipTest(f'Test file not found: {test_file}')

            scanner = IOScanner()
            result = scanner.scan_file(test_file)
            models = result['models']

            weather_model = models.get('AirportWeather', {})
            weather_fields = weather_model.get('fields', {})

            self.assertIn('metar', weather_fields)
            self.assertIn('runways_in_use', weather_fields)

            runways_field = weather_fields.get('runways_in_use', {})
            runways_type = runways_field.get('type')

            self.assertIsInstance(runways_type, dict)
            self.assertEqual(runways_type.get('container'), 'list')
            self.assertEqual(runways_type.get('element_type'), 'Runway')

            metar_model = models.get('METAR', {})
            metar_fields = metar_model.get('fields', {})

            self.assertIn('conditions', metar_fields)

            conditions_field = metar_fields.get('conditions', {})
            conditions_type = conditions_field.get('type')

            self.assertIsInstance(conditions_type, dict)
            self.assertEqual(conditions_type.get('container'), 'list')
            self.assertEqual(conditions_type.get('element_type'), 'WeatherCondition')

            runway_model = models.get('Runway', {})
            runway_fields = runway_model.get('fields', {})

            self.assertIn('coordinates', runway_fields)
            coords_field = runway_fields.get('coordinates', {})
            self.assertEqual(coords_field.get('type'), 'Coordinates')

        finally:
            if services_dir in sys.path:
                sys.path.remove(services_dir)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
