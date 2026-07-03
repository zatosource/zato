from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rqai08() -> str:
    return fake_msh("RQA", "I08", "RQA_I08") + fake_pid()
