# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Make the shared OData test server and the SOAP TLS helpers importable
_tests_python_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(_tests_python_dir, 'zato-common', 'odata', 'lib'))
sys.path.insert(0, os.path.join(_tests_python_dir, 'zato-common', 'soap', 'lib'))

# Zato
from odata_test_server import ODataTestServer, Profile

# ################################################################################################################################
# ################################################################################################################################

def start_odata_server(profile:'str') -> 'ODataTestServer':
    """ Starts an OData test server for the given profile on an ephemeral port.
    """
    server = ODataTestServer(profile)
    server.start()
    return server

# ################################################################################################################################

def seed_business_central(server:'ODataTestServer') -> 'None':
    """ Loads a small, predictable set of Business Central customers.
    """
    server.add_entities('customers', 'id', [
        {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum', 'city': 'Atlanta', 'balanceDue': 100},
        {'id': 'aaaa0002-0000-0000-0000-000000000002', 'displayName': 'Trey Research', 'city': 'Chicago', 'balanceDue': 200},
        {'id': 'aaaa0003-0000-0000-0000-000000000003', 'displayName': 'School of Art', 'city': 'Atlanta', 'balanceDue': 300},
    ])

# ################################################################################################################################

def seed_s4hana(server:'ODataTestServer') -> 'None':
    """ Loads a small, predictable set of S/4HANA sales orders.
    """
    server.add_entities('A_SalesOrder', 'SalesOrder', [
        {'SalesOrder': '1', 'SalesOrderType': 'OR', 'SoldToParty': 'CUST-17', 'TotalNetAmount': 100},
        {'SalesOrder': '2', 'SalesOrderType': 'OR', 'SoldToParty': 'CUST-23', 'TotalNetAmount': 250},
    ])

# ################################################################################################################################
# ################################################################################################################################

# Re-exported for conftest and tests
__all__ = ['ODataTestServer', 'Profile', 'start_odata_server', 'seed_business_central', 'seed_s4hana']

# ################################################################################################################################
# ################################################################################################################################
