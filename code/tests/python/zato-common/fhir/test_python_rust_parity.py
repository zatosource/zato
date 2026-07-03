from __future__ import annotations

import inspect

import pytest

import zato_fhir_r4_0_1_core
import zato.fhir.r4_0_1 as r4
from zato.fhir.tests.fakers import resources as fakers_module


def _get_faker_pairs() -> 'list[tuple]':
    pairs = [] # type: list[tuple]
    for name, func in inspect.getmembers(fakers_module, inspect.isfunction):
        if not name.startswith('fake_'):
            continue
        pairs.append((name, func))
    return sorted(pairs, key=lambda x: x[0])


_FAKER_PAIRS = _get_faker_pairs()
_FAKER_IDS = [p[0] for p in _FAKER_PAIRS]


class TestPythonRustDictParity:

    @pytest.mark.parametrize('name,faker', _FAKER_PAIRS, ids=_FAKER_IDS)
    def test_to_dict_parity(self, name, faker):
        resource = faker()
        py_dict = resource.to_dict()
        rust_dict = zato_fhir_r4_0_1_core.to_dict(resource)
        assert py_dict == rust_dict, (
            f'{name}: Python and Rust to_dict differ'
        )

    @pytest.mark.parametrize('name,faker', _FAKER_PAIRS, ids=_FAKER_IDS)
    def test_from_dict_roundtrip_parity(self, name, faker):
        resource = faker()
        d = zato_fhir_r4_0_1_core.to_dict(resource)
        resource_type = d.get('resourceType', '')
        cls = getattr(r4, resource_type, None)
        if cls is None:
            pytest.skip(f'{resource_type} not in r4 module')
        restored = zato_fhir_r4_0_1_core.from_dict(d, cls)
        d2 = zato_fhir_r4_0_1_core.to_dict(restored)
        assert d == d2, (
            f'{name}: roundtrip dict mismatch'
        )


class TestEmptyResourceParity:

    @pytest.mark.parametrize('name,faker', _FAKER_PAIRS, ids=_FAKER_IDS)
    def test_empty_resource_parity(self, name, faker):
        resource = faker()
        resource_type = resource._resource_type
        cls = getattr(r4, resource_type, None)
        if cls is None:
            pytest.skip(f'{resource_type} not in r4 module')
        empty = cls()
        empty.id = 'parity-empty-test'
        py_dict = empty.to_dict()
        rust_dict = zato_fhir_r4_0_1_core.to_dict(empty)
        assert py_dict == rust_dict, (
            f'{resource_type}: empty resource dicts differ'
        )


class TestRustHandledResources:

    def test_rust_handles_all_python_resources(self):
        py_types = set() # type: set[str]
        for name in dir(r4):
            cls = getattr(r4, name)
            if isinstance(cls, type) and hasattr(cls, '_resource_type') and cls._resource_type:
                py_types.add(cls._resource_type)

        failures = [] # type: list[str]
        for rt in sorted(py_types):
            cls = getattr(r4, rt, None)
            if cls is None:
                continue
            try:
                obj = cls()
                obj.id = 'rust-dispatch-test'
                zato_fhir_r4_0_1_core.to_dict(obj)
            except Exception as exc:
                failures.append(f'{rt}: {exc}')

        assert not failures, (
            f'Rust to_dict failed for {len(failures)} resources:\n' + '\n'.join(failures)
        )
