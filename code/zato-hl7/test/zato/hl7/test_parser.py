# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.hl7.common import Const
from zato.hl7.parser import parse as hl7_parse

# ################################################################################################################################
# ################################################################################################################################

class ParserTestCase(TestCase):

    def test_parser(self):

        data = """
MSH|^~\&|REGADT|MCM|RSP1P8|MCM|203901051530|SEC|ADT^A41^ADT_A39|00000005|P|2.8|
EVN|A41|200301051530
PID|||MR1^^^XYZ||EVERYWOMAN^EVE||19501010|M|||123 NORTH
STREET^^NY^NY^10021||(212)111-3333|||S||ACCT1
MRG|MR1^^^XYZ||ACCT2
""".strip()

        impl_class = Const.ImplClass.hl7apy
        version    = Const.Version.v2

        should_validate    = True
        needs_error_report = True

        result = hl7_parse(data, impl_class, version, should_validate)

        #
        # Check MSH
        #

        msh = result.MSH[0]

        msh_1 = msh.field_separator

        #print(111, msh_1.list)
        #print(222, msh.MSH_1.ST[0])

        #
        # Check EVN
        #

        evn = result.EVN

        #
        # Check PID
        #

        pid = result.PID
        print()
        print(333, dir(pid))
        print(333, pid.list)
        print()

        #
        # Check MRG
        #

        mrg = result.MRG

# ################################################################################################################################
# ################################################################################################################################
