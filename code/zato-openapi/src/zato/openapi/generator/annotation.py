# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import ast
import dataclasses
import typing
from enum import Enum
from inspect import get_annotations, isclass
from types import ModuleType, UnionType

# Zato
from zato.common import typing_ as zato_typing
from zato.openapi.generator.basic_types import Basic_Types

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist
    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The type names of a value of any type and of the value None
Any_Type_Name  = 'any_'
None_Type_Name = 'NoneType'

# The type name of the ellipsis in tuple_[Type, ...], which says that the tuple has any number of elements of that type
_ellipsis_name = '...'

# The container names that annotations use, each with the kind of an OpenAPI schema it is documented as
Container_Kinds = {
    'list': 'list',
    'list_': 'list',
    'List': 'list',
    'Sequence': 'list',
    'MutableSequence': 'list',
    'Iterable': 'list',
    'Collection': 'list',
    'set': 'set',
    'set_': 'set',
    'Set': 'set',
    'frozenset': 'set',
    'FrozenSet': 'set',
    'AbstractSet': 'set',
    'MutableSet': 'set',
    'tuple': 'tuple',
    'tuple_': 'tuple',
    'Tuple': 'tuple',
    'dict': 'dict',
    'dict_': 'dict',
    'Dict': 'dict',
    'Mapping': 'dict',
    'MutableMapping': 'dict',
    'OrderedDict': 'dict',
    'defaultdict': 'dict',
    'DefaultDict': 'dict',
}

# The kinds of containers that the names above stand for
Container_Kind_Names = {'list', 'set', 'tuple', 'dict'}

# The OpenAPI types of the values that enumerations and literals may consist of
JSON_Value_Types = {
    str: 'string',
    bool: 'boolean',
    int: 'integer',
    float: 'number',
    type(None): 'null',
}

# The names of the subscripted forms that are not containers
_optional_names = {'Optional', 'optional'}
_union_names    = {'Union', 'union_'}
_literal_names  = {'Literal'}

# The names and the origins of the forms that only qualify the type that they wrap
_qualifier_names   = {'Annotated', 'ClassVar', 'Final', 'Required', 'NotRequired'}
_qualifier_origins = {typing.Annotated, typing.ClassVar, typing.Final, typing.Required, typing.NotRequired}

# ################################################################################################################################
# ################################################################################################################################

def _get_zato_typing_aliases() -> 'anydict':
    """ Returns the aliases that Zato's typing module defines, which modules often import for type checkers only,
    without the modules that it imports and without aliases that are only text.
    """
    out:'anydict' = {}

    for name, value in vars(zato_typing).items():
        if isinstance(value, ModuleType):
            continue
        if isinstance(value, str):
            continue
        out[name] = value

    return out

# ################################################################################################################################

# The aliases that Zato's typing module defines, by their names
_zato_typing_aliases = _get_zato_typing_aliases()

# ################################################################################################################################
# ################################################################################################################################

def make_container(kind:'str', element_type:'any_') -> 'anydict':
    """ Returns the type of a container of the given kind whose elements, or values in the case of dicts, have the given type.
    """
    out = {'container': kind, 'element_type': element_type}
    return out

# ################################################################################################################################

def make_optional(type_:'any_') -> 'anydict':
    """ Returns the type of a value that is either of the given type or None.
    """
    out = {'type': type_, 'optional': True}
    return out

# ################################################################################################################################

def make_union(members:'anylist') -> 'any_':
    """ Returns the type of a value that is of any of the given types, which is an optional type if one of them is None.
    """
    is_optional = False
    union_types:'anylist' = []

    for member in members:
        if member == None_Type_Name:
            is_optional = True
        elif member not in union_types:
            union_types.append(member)

    type_count = len(union_types)

    # Nothing but None ..
    if type_count == 0:
        out = None_Type_Name

    # .. a single type ..
    elif type_count == 1:
        out = union_types[0]

    # .. or several of them.
    else:
        out = {'type': 'union', 'container': 'union', 'union_types': union_types}

    if is_optional:
        if type_count:
            out = make_optional(out)

    return out

# ################################################################################################################################

def make_enum(values:'anylist') -> 'any_':
    """ Returns the type of a value that is one of the given values, or any type if there are no values
    or a value has no OpenAPI form.
    """
    if not values:
        out = Any_Type_Name
        return out

    for value in values:
        if type(value) not in JSON_Value_Types:
            out = Any_Type_Name
            break
    else:
        out = {'enum': values}

    return out

# ################################################################################################################################

def get_container(kind:'str', argument_types:'anylist') -> 'anydict':
    """ Returns the type of a container of the given kind from the types of the arguments that its annotation has.
    """
    argument_count = len(argument_types)

    # The values of a dict are what the second argument names ..
    if kind == 'dict':
        if argument_count == 2:
            element_type = argument_types[1]
        else:
            element_type = Any_Type_Name

    # .. the elements of a tuple have a type in common only if all the arguments name it ..
    elif kind == 'tuple':
        element_type = _get_tuple_element_type(argument_types)

    # .. and lists and sets have elements of the type that the only argument names.
    elif argument_count:
        element_type = argument_types[0]

    else:
        element_type = Any_Type_Name

    out = make_container(kind, element_type)
    return out

# ################################################################################################################################

def get_io_container(io_type:'any_') -> 'anydict':
    """ Returns the definition of a service's input or output given as a subscripted type, e.g. list_[Model],
    which is a container or, for other subscripted types, input or output of any type.
    """
    # Containers have elements of a type of their own ..
    if isinstance(io_type, dict):
        if kind := io_type.get('container'):
            if kind in Container_Kind_Names:
                out = {
                    'type': 'container',
                    'container_type': kind,
                    'element_type': io_type['element_type'],
                }
                return out

    # .. while other subscripted types, e.g. optional[Model], are of any type.
    out = {'type': 'any'}
    return out

# ################################################################################################################################

def _get_tuple_element_type(argument_types:'anylist') -> 'any_':
    """ Returns the type that all the elements of a tuple have, or any type if the elements differ.
    """
    element_types:'anylist' = []

    for argument_type in argument_types:
        if argument_type == _ellipsis_name:
            continue
        if argument_type not in element_types:
            element_types.append(argument_type)

    type_count = len(element_types)

    if type_count == 1:
        out = element_types[0]
    else:
        out = Any_Type_Name

    return out

# ################################################################################################################################

def is_model_class(class_:'type') -> 'bool':
    """ Whether a class is a model, i.e. a dataclass or a class whose attributes are annotated, documented as an object.
    """
    # Enumerations are documented by their values ..
    if issubclass(class_, Enum):
        out = False

    # .. dataclasses are models, including the ones without fields ..
    elif dataclasses.is_dataclass(class_):
        out = True

    # .. and so are other classes, as long as they annotate their attributes.
    else:
        annotations = get_annotations(class_)
        out = bool(annotations)

    return out

# ################################################################################################################################
# ################################################################################################################################

class NameResolver:
    """ Resolves the names that annotations consist of into the types that the mapper documents.
    """

    def resolve(self, name:'str') -> 'any_':
        """ Returns the type that a name in an annotation stands for.
        """
        # Names that the mapper knows stay as they are ..
        if name in Basic_Types:
            out = name

        # .. the aliases of Zato's typing module are converted into what they stand for ..
        elif name in _zato_typing_aliases:
            alias = _zato_typing_aliases[name]
            out = get_runtime_type(alias, self)

        # .. and any other name is a model or a type that is defined elsewhere.
        else:
            out = name

        return out

# ################################################################################################################################

    def resolve_qualified(self, name_parts:'strlist') -> 'any_':
        """ Returns the type that a qualified name stands for, e.g. decimal.Decimal, which is that of its last part.
        """
        last_part = name_parts[-1]

        out = self.resolve(last_part)
        return out

# ################################################################################################################################

    def on_model(self, class_:'type') -> 'str':
        """ Returns the name under which the mapper finds the given model.
        """
        out = class_.__name__
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_runtime_type(type_hint:'any_', resolver:'NameResolver') -> 'any_':
    """ Returns the type that the mapper documents for an annotation as the interpreter has it at runtime.
    """
    origin = typing.get_origin(type_hint)
    arguments = typing.get_args(type_hint)

    # An annotation in quotes is read the way the source code spells it ..
    if isinstance(type_hint, str):
        out = parse_annotation_text(type_hint, resolver)

    # .. and so is an argument in quotes of a subscripted generic, e.g. the model in list_['Model'] ..
    elif isinstance(type_hint, typing.ForwardRef):
        out = parse_annotation_text(type_hint.__forward_arg__, resolver)

    # .. None stands for its own type ..
    elif type_hint is None:
        out = None_Type_Name

    elif type_hint is type(None):
        out = None_Type_Name

    elif type_hint is Ellipsis:
        out = _ellipsis_name

    elif type_hint is typing.Any:
        out = Any_Type_Name

    # .. optional[Type], union_[Type1, Type2] and Type1 | Type2 are all unions ..
    elif origin is typing.Union:
        out = _get_runtime_union(arguments, resolver)

    elif origin is UnionType:
        out = _get_runtime_union(arguments, resolver)

    # .. a literal is a value out of the ones it lists ..
    elif origin is typing.Literal:
        literal_values = list(arguments)
        out = make_enum(literal_values)

    # .. a qualifier stands for the type that it wraps ..
    elif origin in _qualifier_origins:
        wrapped_type = arguments[0]
        out = get_runtime_type(wrapped_type, resolver)

    # .. a new type is documented as the type that it is derived from ..
    elif isinstance(type_hint, typing.NewType):
        out = get_runtime_type(type_hint.__supertype__, resolver)

    # .. a subscripted generic is a container, e.g. list_[Model] or dict_[str, int] ..
    elif origin is not None:
        out = _get_runtime_generic(origin, arguments, resolver)

    # .. classes are models, enumerations or types such as str or Decimal ..
    elif isclass(type_hint):
        out = _get_runtime_class(type_hint, resolver)

    # .. and anything else, e.g. a type variable, is a value of any type.
    else:
        out = Any_Type_Name

    return out

# ################################################################################################################################

def _get_runtime_union(arguments:'any_', resolver:'NameResolver') -> 'any_':
    """ Returns the type of a union from the arguments that it has at runtime.
    """
    members:'anylist' = []

    for argument in arguments:
        member = get_runtime_type(argument, resolver)
        members.append(member)

    out = make_union(members)
    return out

# ################################################################################################################################

def _get_runtime_generic(origin:'any_', arguments:'any_', resolver:'NameResolver') -> 'any_':
    """ Returns the type of a subscripted generic from its origin and the arguments that it has at runtime.
    """
    origin_name = origin.__name__

    # Generics other than containers, e.g. callables, are values of any type
    if not (kind := Container_Kinds.get(origin_name)):
        out = Any_Type_Name
        return out

    argument_types:'anylist' = []

    for argument in arguments:
        argument_type = get_runtime_type(argument, resolver)
        argument_types.append(argument_type)

    out = get_container(kind, argument_types)
    return out

# ################################################################################################################################

def _get_runtime_class(class_:'type', resolver:'NameResolver') -> 'any_':
    """ Returns the type of a class, which is an enumeration, a model or a type that the mapper knows.
    """
    # An enumeration is a value out of the ones that its members have ..
    if issubclass(class_, Enum):
        enum_values:'anylist' = []

        for member in class_:
            enum_values.append(member.value)

        out = make_enum(enum_values)

    # .. a model is documented under its own name ..
    elif is_model_class(class_):
        out = resolver.on_model(class_)

    # .. and any other class is documented as the closest of its bases that the mapper knows, e.g. a dict subclass as a dict.
    else:
        for base_class in class_.__mro__:
            if base_class.__name__ in Basic_Types:
                out = base_class.__name__
                break
        else:
            out = Any_Type_Name

    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_annotation_text(text:'str', resolver:'NameResolver') -> 'any_':
    """ Returns the type that the mapper documents for an annotation given as the text of the source code.
    """
    text = text.strip()

    # Text that is not an expression is documented as a value of any type ..
    try:
        expression = ast.parse(text, mode='eval')
    except SyntaxError:
        out = Any_Type_Name

    # .. while an expression is parsed node by node.
    else:
        out = parse_annotation(expression.body, resolver)

    return out

# ################################################################################################################################

def parse_annotation(node:'ast.expr', resolver:'NameResolver') -> 'any_':
    """ Returns the type that the mapper documents for an annotation given as a node of the syntax tree.
    """
    node_type = type(node)

    # Nodes of the kinds that annotations consist of have parsers of their own ..
    if parser := _node_parsers.get(node_type):
        out = parser(node, resolver)

    # .. and any other node, e.g. a call, is a value of any type.
    else:
        out = Any_Type_Name

    return out

# ################################################################################################################################

def _parse_name(node:'ast.Name', resolver:'NameResolver') -> 'any_':
    """ Parses a plain name, e.g. str or a model's name.
    """
    if node.id == 'None':
        out = None_Type_Name
    else:
        out = resolver.resolve(node.id)

    return out

# ################################################################################################################################

def _parse_attribute(node:'ast.Attribute', resolver:'NameResolver') -> 'any_':
    """ Parses a name qualified with its module, e.g. decimal.Decimal.
    """
    # The parts of the name, e.g. decimal and Decimal, are collected from the last one to the first one ..
    name_parts:'anylist' = []
    current:'ast.expr' = node

    while isinstance(current, ast.Attribute):
        name_parts.insert(0, current.attr)
        current = current.value

    # .. together with the plain name that it begins with, unless it begins with another expression, e.g. a call ..
    if isinstance(current, ast.Name):
        name_parts.insert(0, current.id)

    out = resolver.resolve_qualified(name_parts)
    return out

# ################################################################################################################################

def _parse_constant(node:'ast.Constant', resolver:'NameResolver') -> 'any_':
    """ Parses a constant, which is None, an annotation in quotes or the ellipsis of a tuple.
    """
    value = node.value

    if value is None:
        out = None_Type_Name

    elif value is Ellipsis:
        out = _ellipsis_name

    elif isinstance(value, str):
        out = parse_annotation_text(value, resolver)

    else:
        out = Any_Type_Name

    return out

# ################################################################################################################################

def _parse_binary_operation(node:'ast.BinOp', resolver:'NameResolver') -> 'any_':
    """ Parses a union such as Type1 | Type2 | None.
    """
    # Only the vertical bar joins types ..
    if not isinstance(node.op, ast.BitOr):
        out = Any_Type_Name
        return out

    # .. and each operand is a type of its own, or a union again.
    member_nodes:'anylist' = []
    _collect_union_members(node, member_nodes)

    members:'anylist' = []

    for member_node in member_nodes:
        member = parse_annotation(member_node, resolver)
        members.append(member)

    out = make_union(members)
    return out

# ################################################################################################################################

def _collect_union_members(node:'ast.expr', member_nodes:'anylist') -> 'None':
    """ Collects the operands of a chain of vertical bars, e.g. the three types of Type1 | Type2 | None.
    """
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.BitOr):
            _collect_union_members(node.left, member_nodes)
            _collect_union_members(node.right, member_nodes)
            return

    member_nodes.append(node)

# ################################################################################################################################

def _parse_subscript(node:'ast.Subscript', resolver:'NameResolver') -> 'any_':
    """ Parses a subscripted form, e.g. list_[Model], optional[str] or dict_[str, int].
    """
    form_name = _get_form_name(node.value)

    # The arguments are a tuple if there are several of them ..
    if isinstance(node.slice, ast.Tuple):
        argument_nodes = node.slice.elts

    # .. or a single node otherwise.
    else:
        argument_nodes = [node.slice]

    # Literals list values rather than types ..
    if form_name in _literal_names:
        out = _parse_literal(argument_nodes)
        return out

    argument_types:'anylist' = []

    for argument_node in argument_nodes:
        argument_type = parse_annotation(argument_node, resolver)
        argument_types.append(argument_type)

    # .. optional[Type] is a union of the type and None ..
    if form_name in _optional_names:
        argument_types.append(None_Type_Name)
        out = make_union(argument_types)

    elif form_name in _union_names:
        out = make_union(argument_types)

    # .. a qualifier stands for the type that it wraps ..
    elif form_name in _qualifier_names:
        out = argument_types[0]

    # .. containers have elements of the types that the arguments name ..
    elif kind := Container_Kinds.get(form_name):
        out = get_container(kind, argument_types)

    # .. and other generics, e.g. callables, are values of any type.
    else:
        out = Any_Type_Name

    return out

# ################################################################################################################################

def _parse_literal(argument_nodes:'anylist') -> 'any_':
    """ Parses the values that a literal lists, all of which are constants.
    """
    literal_values:'anylist' = []

    for argument_node in argument_nodes:

        # A value other than a constant has no OpenAPI form
        if not isinstance(argument_node, ast.Constant):
            out = Any_Type_Name
            break

        literal_values.append(argument_node.value)

    else:
        out = make_enum(literal_values)

    return out

# ################################################################################################################################

def _get_form_name(node:'ast.expr') -> 'str':
    """ Returns the name of a subscripted form, e.g. list_ in list_[Model] or Optional in typing.Optional[str].
    """
    if isinstance(node, ast.Name):
        out = node.id

    elif isinstance(node, ast.Attribute):
        out = node.attr

    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

# The parsers of the kinds of nodes that annotations consist of
_node_parsers:'anydict' = {
    ast.Name: _parse_name,
    ast.Attribute: _parse_attribute,
    ast.Constant: _parse_constant,
    ast.BinOp: _parse_binary_operation,
    ast.Subscript: _parse_subscript,
}

# ################################################################################################################################
# ################################################################################################################################
