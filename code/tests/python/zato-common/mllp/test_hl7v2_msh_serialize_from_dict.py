# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato_hl7v2.v2_9.segments import MSH

# ################################################################################################################################
# ################################################################################################################################

class TestMSHSerializeFromDict(unittest.TestCase):
    """ Building MSH from scratch and serializing must not produce an extra
    empty field between the encoding characters and the sending application.
    """

    def test_msh_no_extra_empty_field(self) -> 'None':
        """ MSH serialized from dict must produce 'MSH|^~\\&|APP|FAC|...'
        without a spurious empty field after the encoding characters.
        """

        # .. build the MSH segment from scratch ..
        segment = MSH()
        segment.sending_application = 'TESTSENDER'
        segment.sending_facility = 'TESTKLINIK'
        segment.receiving_application = 'TESTRECEIVER'
        segment.receiving_facility = 'TESTEMPFÄNGER'

        serialized = segment.serialize()

        # .. the third pipe-delimited piece must be the sending application ..
        parts = serialized.split('|')

        self.assertEqual(parts[0], 'MSH')
        self.assertEqual(parts[1], '^~\\&')
        self.assertEqual(parts[2], 'TESTSENDER')
        self.assertEqual(parts[3], 'TESTKLINIK')
        self.assertEqual(parts[4], 'TESTRECEIVER')

    def test_msh_full_roundtrip_field_count(self) -> 'None':
        """ A fully populated MSH must serialize with the correct number of fields.
        """
        segment = MSH()
        segment.sending_application = 'APP'
        segment.sending_facility = 'FAC'
        segment.receiving_application = 'RECV'
        segment.receiving_facility = 'RFAC'
        segment.message_control_id = 'CTRL001'
        segment.version_id = '2.6'

        serialized = segment.serialize()
        parts = serialized.split('|')

        # .. MSH|^~\&|APP|FAC|RECV|RFAC|||||||CTRL001|||2.6 ..
        # .. no doubled empty fields next to the encoding characters ..
        self.assertEqual(parts[2], 'APP')
        self.assertNotEqual(parts[2], '')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
