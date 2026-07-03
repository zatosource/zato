from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_omso05() -> str:
    return fake_msh("OMS", "O05", "OMS_O05") + fake_pid()
