from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_brpo30() -> str:
    return fake_msh("BRP", "O30", "BRP_O30") + fake_msa()
