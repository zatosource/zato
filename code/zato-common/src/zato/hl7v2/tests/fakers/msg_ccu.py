from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.clinical import fake_rf1


def fake_ccui20() -> str:
    return fake_msh("CCU", "I20", "CCU_I20") + fake_rf1()
