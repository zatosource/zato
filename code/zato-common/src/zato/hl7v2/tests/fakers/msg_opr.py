from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_opro38() -> str:
    return fake_msh("OPR", "O38", "OPR_O38") + fake_msa()
