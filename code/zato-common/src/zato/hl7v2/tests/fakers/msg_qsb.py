from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_qsbq16() -> str:
    return fake_msh("QSB", "Q16", "QSB_Q16") + fake_pid()
