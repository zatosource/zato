from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa, fake_qrd


def fake_adra19() -> str:
    return fake_msh("ADR", "A19", "ADR_A19") + fake_msa() + fake_qrd()
