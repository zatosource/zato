# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The cases-times-boundaries matrix - every corpus case runs through every boundary
that carries its family, plus the invoke-only cases through the invoke boundary.
"""

# stdlib
import unittest

# Test corpus
from boundaries import InvokeBoundary, MLLPBoundary, QueueBridgeBoundary, SchedulerBoundary
from boundaries_http import RESTBoundary, SOAPBoundary
from boundaries_mcp import MCPBoundary
from cases import build_corpus_cases
from cases_invoke import build_invoke_cases

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from boundaries import Boundary
    from cases import PayloadCase
    Boundary = Boundary
    PayloadCase = PayloadCase

# ################################################################################################################################
# ################################################################################################################################

boundary_case_list = list[tuple['Boundary', 'PayloadCase']]

# ################################################################################################################################
# ################################################################################################################################

def build_matrix() -> 'boundary_case_list':
    """ Returns every (boundary, case) pair to run - each boundary takes
    the corpus families it carries, the invoke boundary also takes its own cases.
    """
    corpus_cases = build_corpus_cases()
    invoke_cases = build_invoke_cases()

    invoke_boundary = InvokeBoundary()

    boundaries = [
        RESTBoundary(),
        SOAPBoundary(),
        SchedulerBoundary(),
        MCPBoundary(),
        QueueBridgeBoundary(),
        MLLPBoundary(),
        invoke_boundary,
    ]

    out = []

    for boundary in boundaries:
        for case in corpus_cases:
            if boundary.runs(case):
                out.append((boundary, case))

    for case in invoke_cases:
        out.append((invoke_boundary, case))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadAcrossBoundaries(unittest.TestCase):
    """ One generic test - deliver each case through its boundaries, decode the wire
    and compare against the case's canonical expectation.
    """

    def test_cases_across_boundaries(self) -> 'None':

        for boundary, case in build_matrix():
            with self.subTest(boundary=boundary.name, case=case.name):

                # Deliver the request through the channel's real entry point ..
                wire = boundary.deliver(case)

                # .. decode the wire form back into a dict or a string ..
                result = boundary.decode(wire, case)

                # .. and check it against the case's canonical expectation.
                if case.verify:
                    case.verify(self, result)
                else:
                    expected = boundary.normalize_expected(case.expected)
                    self.assertEqual(result, expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
