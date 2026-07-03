from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rcvo59() -> str:
    return fake_msh("RCV", "O59", "RCV_O59") + fake_pid()
