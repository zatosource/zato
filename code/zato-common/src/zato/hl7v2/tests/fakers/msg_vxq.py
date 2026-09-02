from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_qrd


def fake_vxqv01() -> str:
    return fake_msh("VXQ", "V01", "VXQ_V01") + fake_qrd()
