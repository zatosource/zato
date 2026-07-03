from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_qcnj01() -> str:
    return fake_msh("QCN", "J01", "QCN_J01") + fake_pid()
