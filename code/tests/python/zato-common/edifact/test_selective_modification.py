# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
import zato.edifact.nl # noqa: F401 - registers the MEDLAB and MEDVRI classes

from zato.edifact.envelope import parse_edifact

# ################################################################################################################################
# ################################################################################################################################

# A MEDLAB interchange with one specimen and three determinations.
_interchange = "UNB+UNOA:1+500000101+500000201+260831:0930+2601'\n" + \
    "UNH+2601+MEDLAB:1'\n" + \
    "ZKH+Streeklab Rijnmond+Wytemaweg:80::Rotterdam:3015CN+?+31107033800'\n" + \
    "PID+1975:03:18+V+Dijk:van der:Peters:de::M.++BSN999990019'\n" + \
    "AFD+Klinische chemie'\n" + \
    "ARA+Dr. E. Verhoeven'\n" + \
    "DET+26:08:30+14:15'\n" + \
    "IDE+C+26082254+bloed'\n" + \
    "SEC+HEMATOLOGIE'\n" + \
    "BEP+1+Hemoglobine+8.6++mmol/l+N+8.5+11.0'\n" + \
    "BEP+1+Hematocriet+0.42++l/l+N+0.40+0.50'\n" + \
    "BEP+1+Leukocyten+12.4++10*9/l+H+4.0+10.0'\n" + \
    "UNT+12+2601'\n" + \
    "UNZ+1+2601'"

# ################################################################################################################################
# ################################################################################################################################

class TestSelectiveModification(unittest.TestCase):

    maxDiff = None

    def test_round_trip_is_byte_exact(self) -> None:
        interchange = parse_edifact(_interchange)

        # Nothing was modified, so serialization reproduces the wire text exactly
        self.assertEqual(interchange.serialize(), _interchange)

    def test_reads_do_not_modify(self) -> None:
        interchange = parse_edifact(_interchange)
        msg = interchange.message

        # Reads cache typed segments and composites on the message ..
        _ = msg.pid.sex
        _ = msg.pid.patient_name.married_name
        _ = msg.hospital.institution_name

        for material in msg.materials:
            for determination in material.determinations:
                _ = determination.result

        # .. and the wire text still comes back byte-exact.
        self.assertEqual(interchange.serialize(), _interchange)

    def test_element_assignment(self) -> None:
        interchange = parse_edifact(_interchange)
        msg = interchange.message

        # A direct element assignment
        msg.pid.sex = 'M'

        serialized = interchange.serialize()
        expected = _interchange.replace(
            "PID+1975:03:18+V+Dijk:van der:Peters:de::M.++BSN999990019'",
            "PID+1975:03:18+M+Dijk:van der:Peters:de::M.++BSN999990019'")

        self.assertEqual(serialized, expected)

    def test_component_assignment(self) -> None:
        interchange = parse_edifact(_interchange)
        msg = interchange.message

        # An assignment inside a composite
        msg.pid.patient_name.married_name = 'Jansen'

        serialized = interchange.serialize()
        expected = _interchange.replace(
            "PID+1975:03:18+V+Dijk:van der:Peters:de::M.++BSN999990019'",
            "PID+1975:03:18+V+Jansen:van der:Peters:de::M.++BSN999990019'")

        self.assertEqual(serialized, expected)

    def test_assignment_inside_group(self) -> None:
        interchange = parse_edifact(_interchange)
        msg = interchange.message

        # An assignment on a segment nested inside a repeating group
        material = msg.materials[0]
        material.determinations[2].result = '9.8'

        serialized = interchange.serialize()
        expected = _interchange.replace(
            "BEP+1+Leukocyten+12.4++10*9/l+H+4.0+10.0'",
            "BEP+1+Leukocyten+9.8++10*9/l+H+4.0+10.0'")

        self.assertEqual(serialized, expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
