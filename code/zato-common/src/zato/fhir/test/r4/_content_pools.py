# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# ################################################################################################################################
# ################################################################################################################################

Faker_Locales = ['en_US', 'fr_FR', 'ja_JP']

# ################################################################################################################################
# ################################################################################################################################

Conditions = [
    {'code': 'J30.1',  'system': 'http://hl7.org/fhir/sid/icd-10-cm', 'display': 'Allergic rhinitis due to pollen'},
    {'code': 'H52.1',  'system': 'http://hl7.org/fhir/sid/icd-10-cm', 'display': 'Myopia, mild'},
    {'code': 'E55.9',  'system': 'http://hl7.org/fhir/sid/icd-10-cm', 'display': 'Vitamin D deficiency, resolved'},
    {'code': 'S93.40', 'system': 'http://hl7.org/fhir/sid/icd-10-cm', 'display': 'Sprain of ankle, healing'},
    {'code': 'Z00.00', 'system': 'http://hl7.org/fhir/sid/icd-10-cm', 'display': 'Encounter for general adult medical examination'},
    {'code': 'Z23',    'system': 'http://hl7.org/fhir/sid/icd-10-cm', 'display': 'Encounter for immunization'},
]

# ################################################################################################################################
# ################################################################################################################################

Medications = [
    {'code': '315246', 'system': 'http://www.nlm.nih.gov/research/umls/rxnorm', 'display': 'Multivitamin tablet'},
    {'code': '11253', 'system': 'http://www.nlm.nih.gov/research/umls/rxnorm', 'display': 'Vitamin D3 1000 IU oral tablet'},
    {'code': '1191',  'system': 'http://www.nlm.nih.gov/research/umls/rxnorm', 'display': 'Cetirizine 10 mg oral tablet'},
    {'code': '36567', 'system': 'http://www.nlm.nih.gov/research/umls/rxnorm', 'display': 'Sunscreen SPF 50 topical lotion'},
]

# ################################################################################################################################
# ################################################################################################################################

Vital_Signs = {
    'systolic_bp':  {'code': '8480-6', 'display': 'Systolic blood pressure', 'unit': 'mmHg',    'low': 100, 'high': 130},
    'diastolic_bp': {'code': '8462-4', 'display': 'Diastolic blood pressure', 'unit': 'mmHg',   'low': 60,  'high': 85},
    'heart_rate':   {'code': '8867-4', 'display': 'Heart rate',              'unit': '/min',     'low': 55,  'high': 90},
    'temperature':  {'code': '8310-5', 'display': 'Body temperature',        'unit': 'Cel',      'low': 36.2, 'high': 37.0},
    'resp_rate':    {'code': '9279-1', 'display': 'Respiratory rate',        'unit': '/min',     'low': 12,  'high': 18},
    'oxygen_sat':   {'code': '2708-6', 'display': 'Oxygen saturation',      'unit': '%',        'low': 96,  'high': 100},
    'body_weight':  {'code': '29463-7','display': 'Body weight',             'unit': 'kg',       'low': 55,  'high': 90},
    'body_height':  {'code': '8302-2', 'display': 'Body height',            'unit': 'cm',       'low': 155, 'high': 190},
    'bmi':          {'code': '39156-5','display': 'Body mass index',         'unit': 'kg/m2',    'low': 18.5, 'high': 27.0},
    'head_circum':  {'code': '9843-4', 'display': 'Head circumference',     'unit': 'cm',       'low': 52,  'high': 60},
}

# ################################################################################################################################
# ################################################################################################################################

Lab_Trending_Sequences = {
    'total_cholesterol': {
        'code': '2093-3', 'display': 'Total cholesterol', 'unit': 'mg/dL',
        'system': 'http://loinc.org',
        'values': [210, 195, 182],
    },
    'hdl_cholesterol': {
        'code': '2085-9', 'display': 'HDL cholesterol', 'unit': 'mg/dL',
        'system': 'http://loinc.org',
        'values': [45, 50, 55],
    },
    'ldl_cholesterol': {
        'code': '2089-1', 'display': 'LDL cholesterol', 'unit': 'mg/dL',
        'system': 'http://loinc.org',
        'values': [140, 125, 110],
    },
    'triglycerides': {
        'code': '2571-8', 'display': 'Triglycerides', 'unit': 'mg/dL',
        'system': 'http://loinc.org',
        'values': [180, 160, 140],
    },
    'vitamin_d': {
        'code': '1989-3', 'display': 'Vitamin D', 'unit': 'ng/mL',
        'system': 'http://loinc.org',
        'values': [18, 32, 45],
    },
    'bmi_trend': {
        'code': '39156-5', 'display': 'Body mass index', 'unit': 'kg/m2',
        'system': 'http://loinc.org',
        'values': [26.1, 25.4, 24.8],
    },
    'blood_glucose': {
        'code': '2339-0', 'display': 'Glucose', 'unit': 'mg/dL',
        'system': 'http://loinc.org',
        'values': [95, 92, 88],
    },
}

# ################################################################################################################################
# ################################################################################################################################

Procedures = [
    {'code': 'Z00.00', 'system': 'http://hl7.org/fhir/sid/icd-10-cm', 'display': 'Annual physical examination'},
    {'code': '36228006', 'system': 'http://snomed.info/sct',          'display': 'Ophthalmic examination'},
    {'code': '34043003', 'system': 'http://snomed.info/sct',          'display': 'Dental prophylaxis'},
    {'code': '91251008', 'system': 'http://snomed.info/sct',          'display': 'Physical therapy procedure'},
    {'code': '33879002', 'system': 'http://snomed.info/sct',          'display': 'Administration of vaccine'},
]

# ################################################################################################################################
# ################################################################################################################################

Organizations = [
    'Sunrise Family Practice',
    'Green Valley Pharmacy',
    'Lakeside Wellness Center',
    'Riverstone Medical Group',
    'Harborview Community Clinic',
    'Meadowbrook Health Center',
    'Oakwood Family Medicine',
    'Clinique du Parc',
    'Centre de Bien-Etre Lumiere',
    'Cabinet Medical Soleil',
]

# ################################################################################################################################
# ################################################################################################################################

Goals = [
    'Increase daily steps to 10,000',
    'Maintain healthy BMI between 18.5 and 24.9',
    'Complete physical therapy program',
    'Take daily multivitamin consistently',
    'Achieve vitamin D level above 30 ng/mL',
    'Reduce total cholesterol below 200 mg/dL',
    'Maintain blood pressure below 120/80 mmHg',
    'Complete annual wellness examination',
]

# ################################################################################################################################
# ################################################################################################################################

Clinical_Narratives = {
    'progress_note': [
        'Patient presents for routine annual wellness visit. Vitals within normal limits. '
        'No acute concerns reported. Physical examination unremarkable. '
        'Encouraged continued daily walking and balanced nutrition.',

        'Follow-up visit for vitamin D supplementation review. Patient reports improved energy levels '
        'since starting vitamin D3 1000 IU daily. Lab results show vitamin D level rising from 18 to 32 ng/mL. '
        'Continue current regimen and recheck in six months.',

        'Patient returns for routine cholesterol panel follow-up. Total cholesterol has decreased from '
        '210 to 195 mg/dL with dietary modifications. HDL improving. '
        'Encouraged continued heart-healthy diet and regular exercise.',
    ],
    'discharge_summary': [
        'Patient seen for routine outpatient wellness visit. All screening tests completed. '
        'Immunizations up to date. Next annual visit scheduled in twelve months.',
    ],
    'referral_letter': [
        'Referring patient for physical therapy evaluation following mild ankle sprain during recreational '
        'activity. Patient is otherwise healthy with no significant medical history. '
        'Goal is full recovery and return to normal activity within six weeks.',
    ],
}

# ################################################################################################################################
# ################################################################################################################################

Insurance_Plans = [
    {'type': 'HMO', 'name': 'Sunrise Health HMO',      'copay': 25, 'deductible': 500,  'oop_max': 3000},
    {'type': 'PPO', 'name': 'Valley Choice PPO',        'copay': 30, 'deductible': 1000, 'oop_max': 4500},
    {'type': 'EPO', 'name': 'Lakeside Essential EPO',   'copay': 20, 'deductible': 750,  'oop_max': 3500},
    {'type': 'HMO', 'name': 'Meadowbrook Family HMO',  'copay': 25, 'deductible': 600,  'oop_max': 3200},
    {'type': 'PPO', 'name': 'Oakwood Premier PPO',      'copay': 35, 'deductible': 1500, 'oop_max': 5000},
    {'type': 'EPO', 'name': 'Harborview Value EPO',     'copay': 20, 'deductible': 500,  'oop_max': 3000},
    {'type': 'PPO', 'name': 'Riverstone Select PPO',    'copay': 40, 'deductible': 2000, 'oop_max': 6000},
]

# ################################################################################################################################
# ################################################################################################################################

Race_Categories = [
    {'code': '2106-3', 'display': 'White'},
    {'code': '2054-5', 'display': 'Black or African American'},
    {'code': '2028-9', 'display': 'Asian'},
    {'code': '1002-5', 'display': 'American Indian or Alaska Native'},
    {'code': '2076-8', 'display': 'Native Hawaiian or Other Pacific Islander'},
]

Ethnicity_Categories = [
    {'code': '2135-2', 'display': 'Hispanic or Latino'},
    {'code': '2186-5', 'display': 'Not Hispanic or Latino'},
]

Preferred_Languages = ['en', 'fr', 'ja']
