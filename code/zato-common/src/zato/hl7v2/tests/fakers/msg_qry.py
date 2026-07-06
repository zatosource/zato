from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_qrd


def fake_qrya19() -> str:
    return fake_msh("QRY", "A19", "QRY_A19") + fake_qrd()
