from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_orpo10() -> str:
    return fake_msh("ORP", "O10", "ORP_O10") + fake_msa()
