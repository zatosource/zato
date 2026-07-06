from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_btso31() -> str:
    return fake_msh("BTS", "O31", "BTS_O31") + fake_pid()
