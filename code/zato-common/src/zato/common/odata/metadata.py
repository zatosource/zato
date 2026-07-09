# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# lxml
from lxml import etree

# Zato
from zato.common.odata.common import ODataSyntaxError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The local names of the EDMX elements the parser reads - shared by EDMX 1.0 (OData V2)
# and EDMX 4.0 (OData V4), whose namespaces differ but whose structure does not.
_element_schema = 'Schema'
_element_entity_type = 'EntityType'
_element_entity_set = 'EntitySet'
_element_key = 'Key'
_element_property_ref = 'PropertyRef'
_element_property = 'Property'
_element_navigation_property = 'NavigationProperty'
_element_function_import = 'FunctionImport'
_element_function = 'Function'
_element_action = 'Action'
_element_return_type = 'ReturnType'
_element_parameter = 'Parameter'

# The V2 HTTP method attribute rides in the metadata namespace.
_v2_http_method_attribute = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}HttpMethod'

# ################################################################################################################################
# ################################################################################################################################

property_dict = 'dict[str, EntityProperty]'
navigation_dict = 'dict[str, NavigationProperty]'
entity_type_dict = 'dict[str, EntityType]'
entity_set_dict = 'dict[str, EntitySet]'
operation_dict = 'dict[str, Operation]'
parameter_list = 'list[OperationParameter]'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EntityProperty:
    """ One structural property of an entity type.
    """
    name: 'str' = ''
    type: 'str' = ''
    is_nullable: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class NavigationProperty:
    """ One navigation property of an entity type - target is the V4 target type
    or the V2 relationship name, whichever the document carries.
    """
    name: 'str' = ''
    target: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EntityType:
    """ One entity type - its key property names, structural properties and navigations.
    """
    name: 'str' = ''
    key: 'strlist'
    properties: 'property_dict'
    navigation_properties: 'navigation_dict'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EntitySet:
    """ One entity set and the namespace-qualified name of the entity type it holds.
    """
    name: 'str' = ''
    entity_type: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OperationParameter:
    """ One parameter of a function or action.
    """
    name: 'str' = ''
    type: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Operation:
    """ One callable operation - a V4 function or action, or a V2 function import.
    """
    name: 'str' = ''
    return_type: 'str' = ''
    parameters: 'parameter_list'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ServiceMetadata:
    """ Everything the parser extracts from a $metadata document.
    """
    edmx_version: 'str' = ''
    entity_sets: 'entity_set_dict'
    entity_types: 'entity_type_dict'
    functions: 'operation_dict'
    actions: 'operation_dict'

# ################################################################################################################################

    def entity_type_of(self, entity_set_name:'str') -> 'EntityType':
        """ Returns the entity type of an entity set, resolving the namespace-qualified
        type name the set declares to the simple name the types are keyed by.
        """
        entity_set = self.entity_sets[entity_set_name]

        # The qualified name's last dotted component is the simple type name.
        simple_name = entity_set.entity_type.rpartition('.')[2]

        out = self.entity_types[simple_name]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _local_name(element:'any_') -> 'str':
    """ Returns an element's tag name without its namespace.
    """
    out = etree.QName(element).localname
    return out

# ################################################################################################################################

def _iter_children(element:'any_', local_name:'str') -> 'any_':
    """ Yields the direct children of an element that carry the given local name,
    regardless of which EDMX namespace they are in.
    """
    for child in element:

        # Comments and processing instructions have no QName to speak of.
        if not isinstance(child.tag, str):
            continue

        if _local_name(child) == local_name:
            yield child

# ################################################################################################################################

def _parse_entity_type(element:'any_') -> 'EntityType':
    """ Parses one EntityType element - its key, properties and navigation properties.
    """

    # Our response to produce
    out = EntityType()
    out.key = []
    out.properties = {}
    out.navigation_properties = {}

    out.name = element.get('Name')

    # The key lists the names of the properties that identify an entity.
    for key_element in _iter_children(element, _element_key):
        for property_ref in _iter_children(key_element, _element_property_ref):
            out.key.append(property_ref.get('Name'))

    # Structural properties carry a type and nullability.
    for property_element in _iter_children(element, _element_property):
        entity_property = EntityProperty()
        entity_property.name = property_element.get('Name')
        entity_property.type = property_element.get('Type')
        entity_property.is_nullable = property_element.get('Nullable') != 'false'

        out.properties[entity_property.name] = entity_property

    # Navigation properties point elsewhere - V4 through a Type, V2 through a Relationship.
    for navigation_element in _iter_children(element, _element_navigation_property):
        navigation = NavigationProperty()
        navigation.name = navigation_element.get('Name')
        navigation.target = navigation_element.get('Type') or navigation_element.get('Relationship') or ''

        out.navigation_properties[navigation.name] = navigation

    return out

# ################################################################################################################################

def _parse_operation(element:'any_') -> 'Operation':
    """ Parses one V4 Function or Action element - its parameters and return type.
    """

    # Our response to produce
    out = Operation()
    out.parameters = []

    out.name = element.get('Name')

    for parameter_element in _iter_children(element, _element_parameter):
        parameter = OperationParameter()
        parameter.name = parameter_element.get('Name')
        parameter.type = parameter_element.get('Type')

        out.parameters.append(parameter)

    # The return type is a child element in V4.
    for return_element in _iter_children(element, _element_return_type):
        out.return_type = return_element.get('Type')

    return out

# ################################################################################################################################

def _parse_function_import(element:'any_') -> 'Operation':
    """ Parses one V2 FunctionImport element - its parameters and return type ride
    as attributes rather than child elements.
    """

    # Our response to produce
    out = Operation()
    out.parameters = []

    out.name = element.get('Name')
    out.return_type = element.get('ReturnType') or ''

    for parameter_element in _iter_children(element, _element_parameter):
        parameter = OperationParameter()
        parameter.name = parameter_element.get('Name')
        parameter.type = parameter_element.get('Type')

        out.parameters.append(parameter)

    return out

# ################################################################################################################################

def parse_metadata(data:'bytes') -> 'ServiceMetadata':
    """ Parses a $metadata EDMX document of either version into a ServiceMetadata -
    the element structure is shared between EDMX 1.0 and 4.0, so one walk over
    local names covers both.
    """
    try:
        root = etree.fromstring(data)
    except etree.XMLSyntaxError as e:
        raise ODataSyntaxError(f'Could not parse $metadata -> {e}')

    # Our response to produce
    out = ServiceMetadata()
    out.entity_sets = {}
    out.entity_types = {}
    out.functions = {}
    out.actions = {}

    out.edmx_version = root.get('Version') or ''

    # Schemas live under the DataServices wrapper, whose depth is the same in both versions.
    for schema in root.iter():

        if not isinstance(schema.tag, str):
            continue

        if _local_name(schema) != _element_schema:
            continue

        for child in schema:

            if not isinstance(child.tag, str):
                continue

            child_name = _local_name(child)

            # Entity types carry the keys, properties and navigations.
            if child_name == _element_entity_type:
                entity_type = _parse_entity_type(child)
                out.entity_types[entity_type.name] = entity_type

            # V4 declares functions and actions at the schema level.
            elif child_name == _element_function:
                operation = _parse_operation(child)
                out.functions[operation.name] = operation

            elif child_name == _element_action:
                operation = _parse_operation(child)
                out.actions[operation.name] = operation

        # Entity sets and V2 function imports live inside the entity container.
        for container in schema.iter():

            if not isinstance(container.tag, str):
                continue

            container_name = _local_name(container)

            if container_name == _element_entity_set:
                entity_set = EntitySet()
                entity_set.name = container.get('Name')
                entity_set.entity_type = container.get('EntityType')

                out.entity_sets[entity_set.name] = entity_set

            elif container_name == _element_function_import:

                # A V4 function import merely exposes a schema-level function, which was parsed above.
                if container.get('Function'):
                    continue

                operation = _parse_function_import(container)

                # V2 marks modifying imports with an HTTP method of POST - those are actions.
                http_method = container.get(_v2_http_method_attribute) or 'GET'

                if http_method.upper() == 'GET':
                    out.functions[operation.name] = operation
                else:
                    out.actions[operation.name] = operation

    return out

# ################################################################################################################################
# ################################################################################################################################
