from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.scheduling import fake_sch


def fake_sius12() -> str:
    return fake_msh("SIU", "S12", "SIU_S12") + fake_sch()
