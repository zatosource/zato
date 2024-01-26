# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Monkey-patch first
from gevent import monkey
monkey.patch_all()

# stdlib
import logging
import os
from time import sleep
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# Zato
from zato.common.test import TestCluster, TestParallelServer
from zato.common.typing_ import cast_
from zato.server.generic.api.outconn_hl7_fhir import OutconnHL7FHIRWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odb.api import ODBManager
    ODBManager = ODBManager

# ################################################################################################################################
# ################################################################################################################################

log_level = logging.DEBUG
log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=log_level, format=log_format)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_FHIR_ID = 'Zato_Test_FHIR_ID'
    Env_Key_FHIR_Meta_Last_Updated = 'Zato_Test_FHIR_Meta_Last_Updated'
    Env_Key_FHIR_Username = 'Zato_Test_FHIR_Username'
    Env_Key_FHIR_Password = 'Zato_Test_FHIR_Password'
    Env_Key_FHIR_Address = 'Zato_Test_FHIR_Address'
    Env_Key_FHIR_Person_Given_Name1 = 'Zato_Test_FHIR_Person_Given_Name1'
    Env_Key_FHIR_Person_Given_Name2 = 'Zato_Test_FHIR_Person_Given_Name2'
    Env_Key_FHIR_Person_Family_Name = 'Zato_Test_FHIR_Person_Family_Name'
    Queue_Build_Cap = 0.5

# ################################################################################################################################
# ################################################################################################################################

class HL7FHIRReadTestCase(TestCase):

    def test_hl7_fhir_read(self):

        # Try to get the main environment variable ..
        username = os.environ.get(ModuleCtx.Env_Key_FHIR_Username)

        # .. and if it does not exist, do not run the test
        if not username:
            return

        # If we are here, it means that we can proceed with the test

        # Get the rest of the configuration
        password = os.environ.get(ModuleCtx.Env_Key_FHIR_Password) or 'Missing_Env_Key_FHIR_Password'
        address = os.environ.get(ModuleCtx.Env_Key_FHIR_Address) or 'Missing_Env_Key_FHIR_Password'

        resource_id = os.environ.get(ModuleCtx.Env_Key_FHIR_ID) or 'Missing_Env_Key_FHIR_ID'
        meta_last_updated = os.environ.get(ModuleCtx.Env_Key_FHIR_Meta_Last_Updated) or 'Missing_Env_Key_FHIR_Meta_Last_Updated'

        given_name1 = os.environ.get(ModuleCtx.Env_Key_FHIR_Person_Given_Name1) or 'Missing_Env_Key_FHIR_Person_Given_Name1'
        given_name2 = os.environ.get(ModuleCtx.Env_Key_FHIR_Person_Given_Name2) or 'Missing_Env_Key_FHIR_Person_Given_Name2'
        family_name = os.environ.get(ModuleCtx.Env_Key_FHIR_Person_Family_Name) or 'Missing_Env_Key_FHIR_Person_Family_Name'

        # Build the entire config dictionary that the wrapper expects
        config = bunchify({
            'id': 123,
            'name': 'Wrapper-HL7FHIRReadTestCase',
            'is_active': True,
            'pool_size': 1,
            'queue_build_cap': ModuleCtx.Queue_Build_Cap,
            'address': address,
            'username': username,
            'secret': password,
        })

        # Create a test server
        cluster = TestCluster('Cluster-HL7FHIRReadTestCase')
        odb = cast_('ODBManager', None)
        server_name = 'Server-HL7FHIRReadTestCase'
        server = TestParallelServer(cluster, odb, server_name)

        # Build the wrapper
        wrapper = OutconnHL7FHIRWrapper(config, server)
        wrapper.build_queue()

        # Sleep for a while to ensure that the queue is built
        sleep_time = ModuleCtx.Queue_Build_Cap * 1.1
        sleep(sleep_time)

        # Given, ping the connection
        wrapper.ping()

        # Now, obtain a test resource
        with wrapper.client() as client:

            # We are going to look up patients
            patients = client.resources('Patient') # type: ignore

            # Look for this particular one
            result = patients.search(name__contains=ModuleCtx.Env_Key_FHIR_Person_Given_Name1)

            # Get the patient
            result = result.first()

            # Log information received
            logging.info('FHIR result -> %s', dict(result))

        # Now, check that all the details match

        self.assertFalse(result.active)
        self.assertEqual(result.id, resource_id)
        self.assertEqual(result.resourceType, 'Patient')

        self.assertEqual(result.meta.versionId, '1')
        self.assertEqual(result.meta.lastUpdated, meta_last_updated)

        names = result.name
        self.assertEqual(len(names), 1)

        name = names[0]

        expected_given_names = sorted([given_name1, given_name2])
        received_given_names = sorted(name.given)

        self.assertListEqual(expected_given_names, received_given_names)

        self.assertEqual(name.use, 'official')
        self.assertEqual(name.family, family_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
