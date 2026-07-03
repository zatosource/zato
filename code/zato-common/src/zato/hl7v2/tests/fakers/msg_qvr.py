from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_qvrq17() -> str:
    return fake_msh("QVR", "Q17", "QVR_Q17") + fake_pid()
