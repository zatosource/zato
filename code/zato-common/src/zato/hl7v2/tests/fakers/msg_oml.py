from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_omlo21() -> str:
    return fake_msh("OML", "O21", "OML_O21") + fake_pid()

def fake_omlo33() -> str:
    return fake_msh("OML", "O33", "OML_O33") + fake_pid()

def fake_omlo35() -> str:
    return fake_msh("OML", "O35", "OML_O35") + fake_pid()

def fake_omlo39() -> str:
    return fake_msh("OML", "O39", "OML_O39") + fake_pid()

def fake_omlo59() -> str:
    return fake_msh("OML", "O59", "OML_O59") + fake_pid()
