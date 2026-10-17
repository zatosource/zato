# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.openapi.generator.annotation import NameResolver, parse_annotation_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_resolver = NameResolver()

# The union of two numeric types as the parser returns it
_number_union = {'type': 'union', 'container': 'union', 'union_types': ['int', 'float']}

# ################################################################################################################################
# ################################################################################################################################

def _parse(text:'str') -> 'any_':
    """ Parses an annotation given as the text of the source code.
    """
    out = parse_annotation_text(text, _resolver)
    return out

# ################################################################################################################################
# ################################################################################################################################

class AnnotationTextTestCase(TestCase):
    """ Annotations in quotes, and annotations in scanned source code, are read the way the source code spells them.
    """

    def test_a_plain_name(self) -> 'None':
        self.assertEqual(_parse('str'), 'str')

    def test_a_model_name(self) -> 'None':
        self.assertEqual(_parse('Invoice'), 'Invoice')

    def test_none(self) -> 'None':
        self.assertEqual(_parse('None'), 'NoneType')

    def test_surrounding_whitespace(self) -> 'None':
        self.assertEqual(_parse('  str  '), 'str')

# ################################################################################################################################

    def test_an_optional_type_with_a_vertical_bar(self) -> 'None':
        self.assertEqual(_parse('str | None'), {'type': 'str', 'optional': True})

    def test_none_before_the_type(self) -> 'None':
        self.assertEqual(_parse('None | int'), {'type': 'int', 'optional': True})

    def test_a_union_of_two_types(self) -> 'None':
        self.assertEqual(_parse('int | float'), _number_union)

    def test_a_union_of_two_types_and_none(self) -> 'None':
        self.assertEqual(_parse('int | float | None'), {'type': _number_union, 'optional': True})

    def test_a_type_repeated_in_a_union(self) -> 'None':
        self.assertEqual(_parse('str | str'), 'str')

    def test_the_optional_form(self) -> 'None':
        self.assertEqual(_parse('optional[int]'), {'type': 'int', 'optional': True})
        self.assertEqual(_parse('Optional[int]'), {'type': 'int', 'optional': True})

    def test_the_union_form(self) -> 'None':
        self.assertEqual(_parse('union_[int, float]'), _number_union)
        self.assertEqual(_parse('Union[int, float, None]'), {'type': _number_union, 'optional': True})

    def test_a_qualified_form(self) -> 'None':
        self.assertEqual(_parse('typing.Optional[str]'), {'type': 'str', 'optional': True})

# ################################################################################################################################

    def test_a_list_of_models(self) -> 'None':
        self.assertEqual(_parse('list_[Invoice]'), {'container': 'list', 'element_type': 'Invoice'})

    def test_a_builtin_list(self) -> 'None':
        self.assertEqual(_parse('list[int]'), {'container': 'list', 'element_type': 'int'})

    def test_a_list_of_a_model_in_quotes(self) -> 'None':
        self.assertEqual(_parse("list_['Invoice']"), {'container': 'list', 'element_type': 'Invoice'})

    def test_a_list_of_optional_elements(self) -> 'None':
        expected = {'container': 'list', 'element_type': {'type': 'str', 'optional': True}}
        self.assertEqual(_parse('list_[str | None]'), expected)

    def test_a_list_of_lists(self) -> 'None':
        expected = {'container': 'list', 'element_type': {'container': 'list', 'element_type': 'int'}}
        self.assertEqual(_parse('list_[list_[int]]'), expected)

    def test_a_dict(self) -> 'None':
        self.assertEqual(_parse('dict_[str, int]'), {'container': 'dict', 'element_type': 'int'})

    def test_a_dict_without_arguments(self) -> 'None':
        self.assertEqual(_parse('Dict'), 'Dict')

    def test_a_set(self) -> 'None':
        self.assertEqual(_parse('set_[str]'), {'container': 'set', 'element_type': 'str'})

    def test_a_frozenset(self) -> 'None':
        self.assertEqual(_parse('frozenset[int]'), {'container': 'set', 'element_type': 'int'})

    def test_a_tuple_of_any_length(self) -> 'None':
        self.assertEqual(_parse('tuple_[int, ...]'), {'container': 'tuple', 'element_type': 'int'})

    def test_a_tuple_of_elements_of_one_type(self) -> 'None':
        self.assertEqual(_parse('tuple[str, str]'), {'container': 'tuple', 'element_type': 'str'})

    def test_a_tuple_of_elements_of_different_types(self) -> 'None':
        self.assertEqual(_parse('tuple_[int, str]'), {'container': 'tuple', 'element_type': 'any_'})

# ################################################################################################################################

    def test_a_literal(self) -> 'None':
        self.assertEqual(_parse("Literal['open', 'closed']"), {'enum': ['open', 'closed']})

    def test_a_literal_of_numbers(self) -> 'None':
        self.assertEqual(_parse('Literal[1, 2, 3]'), {'enum': [1, 2, 3]})

    def test_a_literal_of_a_value_without_a_constant(self) -> 'None':
        self.assertEqual(_parse('Literal[Status.Open]'), 'any_')

    def test_an_annotated_type(self) -> 'None':
        self.assertEqual(_parse("Annotated[int, 'Order count']"), 'int')

    def test_a_class_variable(self) -> 'None':
        self.assertEqual(_parse('ClassVar[str]'), 'str')

# ################################################################################################################################

    def test_a_qualified_name(self) -> 'None':
        self.assertEqual(_parse('decimal.Decimal'), 'Decimal')
        self.assertEqual(_parse('datetime.datetime'), 'datetime')

    def test_a_zato_alias_known_to_the_mapper(self) -> 'None':
        self.assertEqual(_parse('strnone'), 'strnone')
        self.assertEqual(_parse('decimal_'), 'decimal_')

    def test_a_zato_alias_converted_into_what_it_stands_for(self) -> 'None':
        self.assertEqual(_parse('intanydict'), {'container': 'dict', 'element_type': 'any_'})
        self.assertEqual(_parse('strsetdict'), {'container': 'dict', 'element_type': {'container': 'set', 'element_type': 'any_'}})

# ################################################################################################################################

    def test_a_callable(self) -> 'None':
        self.assertEqual(_parse('Callable[[int], str]'), 'any_')

    def test_a_call(self) -> 'None':
        self.assertEqual(_parse('get_type()'), 'any_')

    def test_text_that_is_not_an_expression(self) -> 'None':
        self.assertEqual(_parse('list_['), 'any_')
        self.assertEqual(_parse(''), 'any_')

    def test_an_operator_other_than_the_vertical_bar(self) -> 'None':
        self.assertEqual(_parse('int + str'), 'any_')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
