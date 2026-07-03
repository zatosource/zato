from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_qbpe03() -> str:
    return fake_msh("QBP", "E03", "QBP_E03") + fake_pid()

def fake_qbpe22() -> str:
    return fake_msh("QBP", "E22", "QBP_E22") + fake_pid()

def fake_qbpo33() -> str:
    return fake_msh("QBP", "O33", "QBP_O33") + fake_pid()

def fake_qbpo34() -> str:
    return fake_msh("QBP", "O34", "QBP_O34") + fake_pid()

def fake_qbpq11() -> str:
    return fake_msh("QBP", "Q11", "QBP_Q11") + fake_pid()

def fake_qbpq13() -> str:
    return fake_msh("QBP", "Q13", "QBP_Q13") + fake_pid()

def fake_qbpq15() -> str:
    return fake_msh("QBP", "Q15", "QBP_Q15") + fake_pid()

def fake_qbpq21() -> str:
    return fake_msh("QBP", "Q21", "QBP_Q21") + fake_pid()

def fake_qbpqnn() -> str:
    return fake_msh("QBP", "Qnn", "QBP_Qnn") + fake_pid()

def fake_qbpz73() -> str:
    return fake_msh("QBP", "Z73", "QBP_Z73") + fake_pid()
