from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_brto32() -> str:
    return fake_msh("BRT", "O32", "BRT_O32") + fake_msa()
