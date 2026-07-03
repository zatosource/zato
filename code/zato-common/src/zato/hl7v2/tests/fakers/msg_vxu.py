from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_vxuv04() -> str:
    return fake_msh("VXU", "V04", "VXU_V04") + fake_pid()
