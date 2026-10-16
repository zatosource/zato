# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
from dataclasses import dataclass
from typing import NamedTuple

# Zato
from zato.common.typing_ import list_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

class WaitingTimeRow(NamedTuple):
    clinic_code:       str
    days_to_intake:    int
    days_to_treatment: int
    patients_waiting:  int

# ################################################################################################################################
# ################################################################################################################################

class IndicatorRow(NamedTuple):
    name:            str
    target:          float
    actual:          float
    is_lower_better: bool

# ################################################################################################################################
# ################################################################################################################################

# The waiting times per clinic the mock analytics are built from
_waiting_times = [
    WaitingTimeRow('CL-OUT-01', 18, 34, 142),
    WaitingTimeRow('CL-OUT-02', 25, 41, 97),
    WaitingTimeRow('CL-DAY-01', 12, 20, 38),
]

# The indicators a value-based contract is monitored against, each with its target and the measured value
_indicators = [
    IndicatorRow('Median days to treatment',          28.0, 31.5, True),
    IndicatorRow('Outcome measurement response rate', 0.7,  0.74, False),
    IndicatorRow('Improvement in outcome scores',     0.5,  0.56, False),
    IndicatorRow('Readmissions within 90 days',       0.1,  0.08, True),
]

_default_period = '2026-Q3'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ClinicWaitingTime(Model):
    clinic_code:              str
    median_days_to_intake:    int
    median_days_to_treatment: int
    patients_waiting:         int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WaitingTimesResponse(Model):
    period:  str
    clinics: list_[ClinicWaitingTime]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Indicator(Model):
    name:   str
    target: float
    actual: float
    is_met: bool

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ContractPerformance(Model):
    contract_code:  str
    period:         str
    overall_status: str
    indicators:     list_[Indicator]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class DecisionSupportRequest(Model):
    patient_id:         str
    episode_id:         str
    primary_concern:    str
    latest_score:       int
    sessions_completed: int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Recommendation(Model):
    code:           str
    text:           str
    strength:       str
    evidence_level: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RecommendationResponse(Model):
    patient_id:      str
    recommendations: list_[Recommendation]

# ################################################################################################################################
# ################################################################################################################################

class GetWaitingTimes(Service):
    """ Returns the median waiting times to intake and to treatment per clinic.
    """
    name   = 'healthcare.analytics.get-waiting-times'
    input  = '-clinic_code', '-period'
    output = WaitingTimesResponse

    def handle(self) -> 'None':

        clinic_code = self.request.input.clinic_code
        period = self.request.input.period or _default_period

        clinics = []

        for item in _waiting_times:

            if clinic_code:
                if item.clinic_code != clinic_code:
                    continue

            clinic = ClinicWaitingTime()
            clinic.clinic_code = item.clinic_code
            clinic.median_days_to_intake = item.days_to_intake
            clinic.median_days_to_treatment = item.days_to_treatment
            clinic.patients_waiting = item.patients_waiting
            clinics.append(clinic)

        out = WaitingTimesResponse()
        out.period = period
        out.clinics = clinics

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class GetContractPerformance(Service):
    """ Returns the indicators of a value-based care contract and whether each of them meets its target.
    """
    name   = 'healthcare.analytics.get-contract-performance'
    input  = 'contract_code', '-period'
    output = ContractPerformance

    def handle(self) -> 'None':

        indicators = []
        met_count = 0

        for item in _indicators:

            if item.is_lower_better:
                is_met = item.actual <= item.target
            else:
                is_met = item.actual >= item.target

            if is_met:
                met_count += 1

            indicator = Indicator()
            indicator.name = item.name
            indicator.target = item.target
            indicator.actual = item.actual
            indicator.is_met = is_met
            indicators.append(indicator)

        all_met = met_count == len(indicators)

        out = ContractPerformance()
        out.contract_code = self.request.input.contract_code
        out.period = self.request.input.period or _default_period
        out.overall_status = 'on-track' if all_met else 'at-risk'
        out.indicators = indicators

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class RunCareTeamQuery(Service):
    """ Runs a predefined ad-hoc query for a care team, e.g. patients without a recent outcome measurement.
    """
    name = 'healthcare.analytics.run-care-team-query'

    def handle(self) -> 'None':

        if not (query_code := self.request.input.get('query_code')):
            query_code = 'no-recent-measurement'

        rows = [
            {'patient_id': 'PT-100231', 'episode_id': 'EP-PT-100231-1', 'last_measured_on': '2026-04-01'},
            {'patient_id': 'PT-100233', 'episode_id': 'EP-PT-100233-1', 'last_measured_on': '2026-05-12'},
        ]

        self.response.payload = {
            'query_code': query_code,
            'team_code': self.request.input.get('team_code'),
            'row_count': len(rows),
            'rows': rows,
        }

# ################################################################################################################################
# ################################################################################################################################

class GetRecommendations(Service):
    """ Returns treatment recommendations for an episode of care based on its latest outcome score.
    """
    name   = 'healthcare.decision-support.get-recommendations'
    input  = DecisionSupportRequest
    output = RecommendationResponse

    def handle(self) -> 'None':

        latest_score = self.request.input.latest_score

        review = Recommendation()
        review.code = 'REVIEW-PLAN'
        review.text = 'Review the treatment plan with the care team'
        review.strength = 'strong' if latest_score >= 15 else 'conditional'
        review.evidence_level = 'B'

        measure = Recommendation()
        measure.code = 'REMEASURE'
        measure.text = 'Repeat the outcome measurement within four weeks'
        measure.strength = 'conditional'
        measure.evidence_level = 'C'

        out = RecommendationResponse()
        out.patient_id = self.request.input.patient_id
        out.recommendations = [review, measure]

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################
