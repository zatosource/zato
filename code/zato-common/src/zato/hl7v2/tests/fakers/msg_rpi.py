from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rpii01() -> str:
    return fake_msh("RPI", "I01", "RPI_I01") + fake_pid()

def fake_rpii04() -> str:
    return fake_msh("RPI", "I04", "RPI_I04") + fake_pid()
