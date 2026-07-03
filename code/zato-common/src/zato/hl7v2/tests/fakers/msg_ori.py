from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_orio24() -> str:
    return fake_msh("ORI", "O24", "ORI_O24") + fake_msa()
