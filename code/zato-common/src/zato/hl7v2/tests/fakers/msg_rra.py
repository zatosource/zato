from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_rrao18() -> str:
    return fake_msh("RRA", "O18", "RRA_O18") + fake_msa()
