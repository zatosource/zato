# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

import json

from pathlib import Path

from zato.fhir.test.r4._scenarios import Scenario_Names, Scenario_Classes

# ################################################################################################################################
# ################################################################################################################################

_data_dir = Path(__file__).parent / 'data'
_cache = {} # type: dict

# ################################################################################################################################
# ################################################################################################################################

def _load_resource(data:'dict') -> 'object':
    from zato.fhir.r4_0_1 import resources as _r4
    resource_type = data.get('resourceType', '')
    cls = getattr(_r4, resource_type, None)
    if cls is None:
        raise ValueError(f'Unknown FHIR resource type: {resource_type!r}')
    return cls.from_dict(data)

# ################################################################################################################################
# ################################################################################################################################

def _load_scenario_instance(scenario_name:'str', filepath:'Path') -> 'object':
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    cls = Scenario_Classes[scenario_name]
    instance = cls.__new__(cls)

    for field_name in cls.__dataclass_fields__:
        value = raw.get(field_name)
        if value is None:
            continue
        if isinstance(value, list):
            setattr(instance, field_name, [_load_resource(item) for item in value])
        else:
            setattr(instance, field_name, _load_resource(value))

    return instance

# ################################################################################################################################
# ################################################################################################################################

def _load_all() -> 'tuple[dict, dict]':
    scenarios = {} # type: dict[str, list]
    resources = {} # type: dict[str, list]

    for name in Scenario_Names:
        sdir = _data_dir / name
        if not sdir.exists():
            continue

        instances = [] # type: list
        for fp in sorted(sdir.glob('*.json')):
            inst = _load_scenario_instance(name, fp)
            instances.append(inst)

            for field in type(inst).__dataclass_fields__:
                val = getattr(inst, field, None)
                if val is None:
                    continue
                items = val if isinstance(val, list) else [val]
                for item in items:
                    rt = getattr(type(item), '_resource_type', type(item).__name__)
                    resources.setdefault(rt, []).append(item)

        if instances:
            scenarios[name] = instances

    return scenarios, resources

# ################################################################################################################################
# ################################################################################################################################

def _ensure_loaded():
    if 'done' not in _cache:
        _cache['scenarios'], _cache['resources'] = _load_all()
        _cache['done'] = True

# ################################################################################################################################
# ################################################################################################################################

class _TestDataMeta(type):
    def __getattr__(cls, name:'str'):
        if name.startswith('_'):
            raise AttributeError(name)
        _ensure_loaded()
        return _cache['resources'].get(name, [])

# ################################################################################################################################
# ################################################################################################################################

class _ScenariosMeta(type):
    def __getattr__(cls, name:'str'):
        if name.startswith('_'):
            raise AttributeError(name)
        _ensure_loaded()
        result = _cache['scenarios'].get(name)
        if result is not None:
            return result
        raise AttributeError(f'Scenarios has no scenario {name!r}')

# ################################################################################################################################
# ################################################################################################################################

class TestData(metaclass=_TestDataMeta):
    """ Access test data by resource type. Each attribute is a list of typed resource objects.

    Usage::

        from zato.fhir.test.r4.v1 import TestData

        patients = TestData.Patient              # list[Patient]
        encounters = TestData.Encounter          # list[Encounter]
        observations = TestData.Observation      # list[Observation]

        for patient in TestData.Patient:
            print(patient.name)
    """

# ################################################################################################################################
# ################################################################################################################################

class Scenarios(metaclass=_ScenariosMeta):
    """ Access test data by scenario name. Each attribute is a list of scenario dataclass instances.

    Usage::

        from zato.fhir.test.r4.v1 import Scenarios

        for scenario in Scenarios.wellness_visit:
            print(scenario.patient.name)
            print(scenario.practitioner.name)
    """

# ################################################################################################################################
# ################################################################################################################################
