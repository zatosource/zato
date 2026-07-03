from __future__ import annotations


from zato.fhir.base import FHIRElement, _resolve_type
from zato.fhir.r4_0_1.datatypes import BackboneElement


class TestBackboneElementExists:

    def test_resolve_type_finds_backbone_element(self):
        cls = _resolve_type('BackboneElement')
        assert cls is BackboneElement

    def test_is_subclass_of_fhir_element(self):
        assert issubclass(BackboneElement, FHIRElement)

    def test_instantiation_default(self):
        be = BackboneElement()
        assert be.id is None


class TestBackboneElementFields:

    def test_list_fields_include_extension_and_modifier(self):
        assert 'extension' in BackboneElement._list_fields
        assert 'modifierExtension' in BackboneElement._list_fields

    def test_field_types_include_extension_and_modifier(self):
        assert BackboneElement._field_types['extension'] == 'Extension'
        assert BackboneElement._field_types['modifierExtension'] == 'Extension'


class TestBackboneElementSetAndGet:

    def test_set_id(self):
        be = BackboneElement()
        be.id = 'be-1'
        assert be.id == 'be-1'

    def test_set_extension_list(self):
        be = BackboneElement()
        be.extension = [
            {'url': 'http://example.org/ext', 'valueString': 'hello'},
        ]
        assert len(be.extension) == 1

    def test_set_modifier_extension_list(self):
        be = BackboneElement()
        be.modifierExtension = [
            {'url': 'http://example.org/mod', 'valueBoolean': True},
        ]
        assert len(be.modifierExtension) == 1


class TestBackboneElementRoundTrip:

    def test_to_dict_with_id_only(self):
        be = BackboneElement()
        be.id = 'rt-1'
        d = be.to_dict()
        assert d == {'id': 'rt-1'}

    def test_to_dict_with_extension(self):
        be = BackboneElement()
        be.id = 'rt-2'
        be.extension = [
            {'url': 'http://example.org/ext', 'valueString': 'test'},
        ]
        d = be.to_dict()
        assert d['id'] == 'rt-2'
        assert len(d['extension']) == 1
        assert d['extension'][0]['url'] == 'http://example.org/ext'
        assert d['extension'][0]['valueString'] == 'test'

    def test_empty_backbone_element_produces_empty_dict(self):
        be = BackboneElement()
        d = be.to_dict()
        assert d == {}
