from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_dero44() -> str:
    return fake_msh("DER", "O44", "DER_O44") + fake_pid()
