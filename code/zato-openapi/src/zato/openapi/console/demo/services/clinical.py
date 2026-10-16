# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
from dataclasses import dataclass
from typing import NamedTuple

# Zato
from zato.common.typing_ import list_, optional
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

class QuestionnaireRow(NamedTuple):
    code:       str
    title:      str
    item_count: int
    max_score:  int

# ################################################################################################################################
# ################################################################################################################################

# The questionnaires the mock outcome measurements are built from
_questionnaires = [
    QuestionnaireRow('MOOD-9',  'Mood Symptom Scale',        9,  27),
    QuestionnaireRow('ANX-7',   'Anxiety Symptom Scale',     7,  21),
    QuestionnaireRow('FUNC-12', 'Daily Functioning Index',   12, 48),
    QuestionnaireRow('EXP-10',  'Patient Experience Survey', 10, 50),
]

# Score thresholds from the highest down, each with the severity it starts at
_severity_thresholds = [(20, 'severe'), (15, 'moderately severe'), (10, 'moderate'), (5, 'mild'), (0, 'minimal')]

_measured_on = ['2026-04-01', '2026-07-01', '2026-10-01']

_timestamp = '2026-10-16T09:30:00+00:00'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Questionnaire(Model):
    code:       str
    title:      str
    item_count: int
    max_score:  int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class QuestionnaireListResponse(Model):
    questionnaires: list_[Questionnaire]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Answer(Model):
    item_code: str
    value:     int

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class SubmitResponseRequest(Model):
    questionnaire_code: str
    patient_id:         str
    episode_id:         str
    completed_at:       str
    answers:            list_[Answer]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SubmitResponseResult(Model):
    response_id: str
    total_score: int
    severity:    str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutcomeScore(Model):
    questionnaire_code:   str
    measured_on:          str
    total_score:          int
    change_from_baseline: int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutcomeScoresResponse(Model):
    patient_id: str
    scores:     list_[OutcomeScore]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AddNoteRequest(Model):
    patient_id:      str
    author_id:       str
    note_type:       str
    text:            str
    episode_id:      optional[str] = None
    is_confidential: bool = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RiskFactor(Model):
    name:  str
    level: str
    notes: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RiskAssessment(Model):
    patient_id:     str
    assessed_on:    str
    assessed_by:    str
    overall_level:  str
    factors:        list_[RiskFactor]
    next_review_on: str

# ################################################################################################################################
# ################################################################################################################################

def _get_severity(total_score:'int') -> 'str':
    """ Returns the severity band a total score falls into.
    """
    for threshold, severity in _severity_thresholds:
        if total_score >= threshold:
            out = severity
            break
    else:
        out = 'minimal'

    return out

# ################################################################################################################################
# ################################################################################################################################

class ListQuestionnaires(Service):
    """ Returns the questionnaires available for routine outcome measurement.
    """
    name   = 'healthcare.outcomes.list-questionnaires'
    input  = '-language'
    output = QuestionnaireListResponse

    def handle(self) -> 'None':

        questionnaires = []

        for item in _questionnaires:
            questionnaire = Questionnaire()
            questionnaire.code = item.code
            questionnaire.title = item.title
            questionnaire.item_count = item.item_count
            questionnaire.max_score = item.max_score
            questionnaires.append(questionnaire)

        out = QuestionnaireListResponse()
        out.questionnaires = questionnaires

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class SubmitQuestionnaireResponse(Service):
    """ Stores a completed questionnaire and returns its total score and the severity band.
    """
    name   = 'healthcare.outcomes.submit-response'
    input  = SubmitResponseRequest
    output = SubmitResponseResult

    def handle(self) -> 'None':

        total_score = 0

        for answer in self.request.input.answers:
            total_score += answer.value

        out = SubmitResponseResult()
        out.response_id = 'QR-880412'
        out.total_score = total_score
        out.severity = _get_severity(total_score)

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class GetOutcomeScores(Service):
    """ Returns the outcome scores of a patient over time, optionally for one questionnaire only.
    """
    name   = 'healthcare.outcomes.get-outcome-scores'
    input  = 'patient_id', '-questionnaire_code'
    output = OutcomeScoresResponse

    def handle(self) -> 'None':

        questionnaire_code = self.request.input.questionnaire_code or 'MOOD-9'
        baseline = 19

        scores = []

        for index, measured_on in enumerate(_measured_on):
            total_score = baseline - index * 5

            score = OutcomeScore()
            score.questionnaire_code = questionnaire_code
            score.measured_on = measured_on
            score.total_score = total_score
            score.change_from_baseline = total_score - baseline
            scores.append(score)

        out = OutcomeScoresResponse()
        out.patient_id = self.request.input.patient_id
        out.scores = scores

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class AddClinicalNote(Service):
    """ Adds a clinical note to the record of a patient.
    """
    name   = 'healthcare.clinical.add-note'
    input  = AddNoteRequest
    output = 'note_id', 'created_at'

    def handle(self) -> 'None':
        self.response.payload.note_id = 'NT-330918'
        self.response.payload.created_at = _timestamp

# ################################################################################################################################
# ################################################################################################################################

class GetRiskAssessment(Service):
    """ Returns the most recent structured risk assessment of a patient.
    """
    name   = 'healthcare.clinical.get-risk-assessment'
    input  = 'patient_id'
    output = RiskAssessment

    def handle(self) -> 'None':

        adherence = RiskFactor()
        adherence.name = 'Treatment adherence'
        adherence.level = 'medium'
        adherence.notes = 'Two missed appointments in the last quarter'

        support = RiskFactor()
        support.name = 'Social support'
        support.level = 'low'
        support.notes = 'Lives with family, regular contact with the care team'

        out = RiskAssessment()
        out.patient_id = self.request.input.patient_id
        out.assessed_on = '2026-10-01'
        out.assessed_by = 'PR-2002'
        out.overall_level = 'medium'
        out.factors = [adherence, support]
        out.next_review_on = '2027-01-01'

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class SubmitChecklist(Service):
    """ Accepts a completed staff checklist, e.g. a shift handover or a medication round.
    """
    name = 'healthcare.clinical.submit-checklist'

    def handle(self) -> 'None':

        if not (items := self.request.input.get('items')):
            items = []

        completed = 0

        for item in items:
            if item.get('is_done'):
                completed += 1

        self.response.payload = {
            'checklist_id': 'CK-4410',
            'items_total': len(items),
            'items_completed': completed,
            'received_at': _timestamp,
        }

# ################################################################################################################################
# ################################################################################################################################
