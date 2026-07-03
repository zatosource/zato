from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_orar33() -> str:
    return fake_msh("ORA", "R33", "ORA_R33") + fake_msa()

def fake_orar41() -> str:
    return fake_msh("ORA", "R41", "ORA_R41") + fake_msa()
