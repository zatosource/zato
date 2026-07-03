from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rtbk13() -> str:
    return fake_msh("RTB", "K13", "RTB_K13") + fake_pid()

def fake_rtbknn() -> str:
    return fake_msh("RTB", "Knn", "RTB_Knn") + fake_pid()

def fake_rtbz74() -> str:
    return fake_msh("RTB", "Z74", "RTB_Z74") + fake_pid()
