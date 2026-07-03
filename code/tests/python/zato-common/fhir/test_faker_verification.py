from __future__ import annotations

import inspect

import pytest

from zato.fhir.base import FHIRResource
from zato.fhir.tests.fakers import resources as fakers_module


def _iter_fake_callables():
    members = inspect.getmembers(fakers_module, inspect.isfunction)
    for name, fn in sorted(members, key=lambda x: x[0]):
        if name.startswith('fake_'):
            yield name, fn


_FAKE_PARAMS = list(_iter_fake_callables())


@pytest.mark.parametrize(
    'fake_fn',
    [fn for _, fn in _FAKE_PARAMS],
    ids=[name for name, _ in _FAKE_PARAMS],
)
def test_fake_resource_roundtrip(fake_fn):
    result = fake_fn()
    assert isinstance(result, FHIRResource)
    assert getattr(result, '_resource_type', None)
    d = result.to_dict()
    assert 'resourceType' in d
    roundtripped = type(result).from_dict(d)
    d2 = roundtripped.to_dict()
    assert d2.get('resourceType') == d.get('resourceType')
