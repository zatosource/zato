# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.api import HL7
from zato.hl7.parser import get_payload_from_request

# ################################################################################################################################
# ################################################################################################################################

class ParserTestCase(TestCase):

    def test_get_payload_from_request(self):

        data = """
MSH|^~\&|MegaReg|XYZHospC|SuperOE|XYZImgCtr|20060529090131-0500||ADT^A01^ADT_A01|01052901|P|2.5
EVN||200605290901||||200605290900
PID|||56782445^^^UAReg^PI||KLEINSAMPLE^BARRY^Q^JR||19620910|M||2028-9^^HL70005^RA99113^^XYZ|260 GOODWIN CREST DRIVE^^BIRMINGHAM^AL^35209^^M~NICKELL’S PICKLES^10000 W 100TH AVE^BIRMINGHAM^AL^35200^^O|||||||0105I30001^^^99DEF^AN
PV1||I|W^389^1^UABH^^^^3||||12345^MORGAN^REX^J^^^MD^0010^UAMC^L||67890^GRAINGER^LUCY^X^^^MD^0010^UAMC^L|MED|||||A0||13579^POTTER^SHERMAN^T^^^MD^0010^UAMC^L|||||||||||||||||||||||||||200605290900
""".strip().replace('\n', '\r')

        f = open('/tmp/hl7.txt', 'wb')
        f.write(data.encode('utf8'))
        f.close()

        version    = HL7.Const.Version.v2.id

        data_encoding         = 'utf8'
        json_path             = None
        should_parse_on_input = True
        should_validate       = True

        result = get_payload_from_request(data, data_encoding, version, json_path, should_parse_on_input, should_validate)

        #
        # Check MSH
        #

        msh = result.MSH
        self.assertEquals(msh.field_separator.value, '|')

        #
        # Check EVN
        #

        evn = result.EVN
        self.assertEquals(evn.recorded_date_time.value, '200605290901')

        #
        # Check PID
        #

        pid = result.PID
        self.assertEquals(pid.patient_address.city.value, 'BIRMINGHAM')

        #
        # Check PV1
        #

        pv1 = result.PV1
        self.assertEquals(pv1.assigned_patient_location.facility.value, 'UABH')

# ################################################################################################################################
# ################################################################################################################################
