# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.api import HL7
from zato.common.test.hl7_ import test_data
from zato.hl7.parser import get_payload_from_request

# ################################################################################################################################
# ################################################################################################################################

class ParserTestCase(TestCase):

    def test_get_payload_from_request(self):

        version    = HL7.Const.Version.v2.id
        data_encoding         = 'utf8'
        json_path             = None
        should_parse_on_input = True
        should_validate       = True

        result = get_payload_from_request(test_data, data_encoding, version, json_path, should_parse_on_input, should_validate)

        #
        # Check MSH
        #

        msh = result.MSH
        self.assertEqual(msh.field_separator.value, '|')

        #
        # Check EVN
        #

        evn = result.EVN
        self.assertEqual(evn.recorded_date_time.value, '200605290901')

        #
        # Check PID
        #

        pid = result.PID
        self.assertEqual(pid.patient_address.city.value, 'BIRMINGHAM')

        #
        # Check PV1
        #

        pv1 = result.PV1
        self.assertEqual(pv1.assigned_patient_location.facility.value, 'UABH')

# ################################################################################################################################
# ################################################################################################################################
