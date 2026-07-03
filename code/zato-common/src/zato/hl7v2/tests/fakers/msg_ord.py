from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_ordo04() -> str:
    return fake_msh("ORD", "O04", "ORD_O04") + fake_msa()
