from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_osuo51() -> str:
    return fake_msh("OSU", "O51", "OSU_O51") + fake_pid()

def fake_osuo52() -> str:
    return fake_msh("OSU", "O52", "OSU_O52") + fake_msa()
