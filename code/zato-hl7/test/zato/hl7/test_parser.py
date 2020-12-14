# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.api import HL7
from zato.hl7.parser import parse as hl7_parse

# ################################################################################################################################
# ################################################################################################################################

class ParserTestCase(TestCase):

    def test_parser(self):

        data = """
MSH|^~\&|REGADT|MCM|RSP1P8|MCM|203901051530|SEC|ADT^A41^ADT_A39|00000005|P|2.8|
EVN|A41|200301051530
PID|11|22|MR1^^^XYZ||EVERYWOMAN^EVE||19501010|M|||123 NORTH STREET^^NY^NY^10021||(212)111-3333|||S||ACCT1
MRG|MR1^^^XYZ||ACCT2
""".strip()

        impl_class = HL7.Const.ImplClass.hl7apy
        version    = HL7.Const.Version.v2.id

        should_validate    = True
        needs_error_report = True

        result = hl7_parse(data, impl_class, version, should_validate)

        #
        # Check MSH
        #

        msh = result.MSH[0]
        self.assertEquals(msh.field_separator.value, '|')

        #
        # Check EVN
        #

        evn = result.EVN

        print()
        print(111, evn)
        print(222, dir(evn))
        print()

        #
        # Check PID
        #

        pid = result.pid


        print()
        print(444, repr(pid.element_name), repr(pid.value))
        print()

        #
        # Check MRG
        #

        mrg = result.MRG

# ################################################################################################################################
# ################################################################################################################################
