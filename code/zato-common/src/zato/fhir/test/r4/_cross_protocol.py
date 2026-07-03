# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

#  Maps FHIR scenario instance IDs to HL7v2 message instance IDs
#  for scenarios that exist in both protocols.

Cross_Protocol_Scenarios = [
    'wellness_visit',
    'immunization_visit',
    'lab_panel',
    'medication_refill',
    'appointment_booking',
]
