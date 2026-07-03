from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_rrdo14() -> str:
    return fake_msh("RRD", "O14", "RRD_O14") + fake_msa()
