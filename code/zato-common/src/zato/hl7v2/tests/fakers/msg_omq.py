from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_omqo57() -> str:
    return fake_msh("OMQ", "O57", "OMQ_O57") + fake_pid()
