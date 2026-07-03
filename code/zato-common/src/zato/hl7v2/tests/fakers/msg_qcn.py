from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment


def fake_qcnj01() -> str:
    return fake_msh("QCN", "J01", "QCN_J01") + fake_segment("QID")
