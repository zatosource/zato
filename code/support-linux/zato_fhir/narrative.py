from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from html import escape

from zato_fhir.base import FHIRResource, FHIRElement


IRREGULAR_PLURALS = {
    'child': 'children',
    'person': 'people',
    'man': 'men',
    'woman': 'women',
    'foot': 'feet',
    'tooth': 'teeth',
    'goose': 'geese',
    'mouse': 'mice',
    'louse': 'lice',
    'ox': 'oxen',
    'criterion': 'criteria',
    'phenomenon': 'phenomena',
    'datum': 'data',
    'medium': 'media',
    'analysis': 'analyses',
    'diagnosis': 'diagnoses',
    'thesis': 'theses',
    'crisis': 'crises',
    'appendix': 'appendices',
    'index': 'indices',
    'matrix': 'matrices',
    'vertex': 'vertices',
    'stimulus': 'stimuli',
    'focus': 'foci',
    'fungus': 'fungi',
    'nucleus': 'nuclei',
    'radius': 'radii',
    'cactus': 'cacti',
    'alumnus': 'alumni',
    'syllabus': 'syllabi',
    'leaf': 'leaves',
    'life': 'lives',
    'knife': 'knives',
    'wife': 'wives',
    'self': 'selves',
    'shelf': 'shelves',
    'half': 'halves',
    'calf': 'calves',
    'loaf': 'loaves',
    'wolf': 'wolves',
}


def pluralize(word: str, count: int) -> str:
    """Return singular or plural form based on count."""
    if count == 1:
        return word
    
    lower = word.lower()
    if lower in IRREGULAR_PLURALS:
        if word[0].isupper():
            return IRREGULAR_PLURALS[lower].capitalize()
        return IRREGULAR_PLURALS[lower]
    
    if lower.endswith('s') or lower.endswith('x') or lower.endswith('z') or lower.endswith('ch') or lower.endswith('sh'):
        return word + 'es'
    if lower.endswith('y') and len(lower) > 1 and lower[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    
    return word + 's'


def count_with_noun(count: int, singular: str) -> str:
    """Return count with properly pluralized noun."""
    return f'{count} {pluralize(singular, count)}'


@dataclass
class NarrativeTemplate:
    fields: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    formatters: dict[str, callable] = field(default_factory=dict)


def format_human_name(value: Any) -> str:
    """Format HumanName to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        parts = []
        family = value.get('family', '')
        given = value.get('given', [])
        prefix = value.get('prefix', [])
        suffix = value.get('suffix', [])
        
        if prefix:
            parts.extend(prefix if isinstance(prefix, list) else [prefix])
        if given:
            parts.extend(given if isinstance(given, list) else [given])
        if family:
            parts.append(family)
        if suffix:
            parts.extend(suffix if isinstance(suffix, list) else [suffix])
        
        return ' '.join(parts)
    
    if hasattr(value, 'family'):
        parts = []
        if hasattr(value, 'prefix') and value.prefix:
            parts.extend(value.prefix if isinstance(value.prefix, list) else [value.prefix])
        if hasattr(value, 'given') and value.given:
            parts.extend(value.given if isinstance(value.given, list) else [value.given])
        if value.family:
            parts.append(value.family)
        if hasattr(value, 'suffix') and value.suffix:
            parts.extend(value.suffix if isinstance(value.suffix, list) else [value.suffix])
        return ' '.join(parts)
    
    return str(value)


def format_codeable_concept(value: Any) -> str:
    """Format CodeableConcept to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        if value.get('text'):
            return value['text']
        codings = value.get('coding', [])
        if codings and isinstance(codings, list) and len(codings) > 0:
            coding = codings[0]
            if isinstance(coding, dict):
                return coding.get('display', '') or coding.get('code', '')
        return ''
    
    if hasattr(value, 'text') and value.text:
        return value.text
    if hasattr(value, 'coding') and value.coding:
        coding = value.coding[0] if isinstance(value.coding, list) else value.coding
        if hasattr(coding, 'display') and coding.display:
            return coding.display
        if hasattr(coding, 'code'):
            return coding.code or ''
    
    return str(value)


def format_coding(value: Any) -> str:
    """Format Coding to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        return value.get('display', '') or value.get('code', '')
    
    if hasattr(value, 'display') and value.display:
        return value.display
    if hasattr(value, 'code'):
        return value.code or ''
    
    return str(value)


def format_identifier(value: Any) -> str:
    """Format Identifier to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        system = value.get('system', '')
        val = value.get('value', '')
        type_text = ''
        if value.get('type'):
            type_text = format_codeable_concept(value['type'])
        
        if type_text and val:
            return f'{type_text}: {val}'
        if val:
            return val
        return ''
    
    if hasattr(value, 'value') and value.value:
        type_text = ''
        if hasattr(value, 'type') and value.type:
            type_text = format_codeable_concept(value.type)
        if type_text:
            return f'{type_text}: {value.value}'
        return value.value
    
    return str(value)


def format_reference(value: Any) -> str:
    """Format Reference to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        if value.get('display'):
            return value['display']
        if value.get('reference'):
            return value['reference']
        return ''
    
    if hasattr(value, 'display') and value.display:
        return value.display
    if hasattr(value, 'reference') and value.reference:
        return value.reference
    
    return str(value)


def format_period(value: Any) -> str:
    """Format Period to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        start = value.get('start', '')
        end = value.get('end', '')
        if start and end:
            return f'{start} to {end}'
        if start:
            return f'from {start}'
        if end:
            return f'until {end}'
        return ''
    
    if hasattr(value, 'start') or hasattr(value, 'end'):
        start = getattr(value, 'start', '') or ''
        end = getattr(value, 'end', '') or ''
        if start and end:
            return f'{start} to {end}'
        if start:
            return f'from {start}'
        if end:
            return f'until {end}'
    
    return str(value)


def format_quantity(value: Any) -> str:
    """Format Quantity to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        val = value.get('value', '')
        unit = value.get('unit', '') or value.get('code', '')
        if val and unit:
            return f'{val} {unit}'
        if val:
            return str(val)
        return ''
    
    if hasattr(value, 'value'):
        val = value.value or ''
        unit = getattr(value, 'unit', '') or getattr(value, 'code', '') or ''
        if val and unit:
            return f'{val} {unit}'
        if val:
            return str(val)
    
    return str(value)


def format_address(value: Any) -> str:
    """Format Address to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        parts = []
        for line in value.get('line', []):
            parts.append(line)
        city = value.get('city', '')
        state = value.get('state', '')
        postal = value.get('postalCode', '')
        country = value.get('country', '')
        
        city_line = ', '.join(filter(None, [city, state, postal]))
        if city_line:
            parts.append(city_line)
        if country:
            parts.append(country)
        
        return ', '.join(parts)
    
    return str(value)


def format_contact_point(value: Any) -> str:
    """Format ContactPoint to readable string."""
    if value is None:
        return ''
    
    if isinstance(value, dict):
        system = value.get('system', '')
        val = value.get('value', '')
        use = value.get('use', '')
        
        parts = []
        if system:
            parts.append(system)
        if val:
            parts.append(val)
        if use:
            parts.append(f'({use})')
        
        return ' '.join(parts)
    
    return str(value)


def format_value(value: Any, field_type: str) -> str:
    """Format a value based on its FHIR type."""
    if value is None:
        return ''
    
    formatters = {
        'HumanName': format_human_name,
        'CodeableConcept': format_codeable_concept,
        'Coding': format_coding,
        'Identifier': format_identifier,
        'Reference': format_reference,
        'Period': format_period,
        'Quantity': format_quantity,
        'Address': format_address,
        'ContactPoint': format_contact_point,
        'Age': format_quantity,
        'Duration': format_quantity,
        'Count': format_quantity,
        'Distance': format_quantity,
        'Money': format_quantity,
    }
    
    if field_type in formatters:
        return formatters[field_type](value)
    
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    
    if isinstance(value, (dict, FHIRElement)):
        return str(value)
    
    return str(value)


def to_label(field_name: str) -> str:
    """Convert field name to human-readable label."""
    result = []
    for i, c in enumerate(field_name):
        if c.isupper() and i > 0:
            result.append(' ')
        result.append(c)
    label = ''.join(result)
    return label[0].upper() + label[1:] if label else ''


def generate_narrative(
    resource: FHIRResource,
    template: NarrativeTemplate | None = None,
) -> dict:
    """
    Generate XHTML narrative for a FHIR resource.
    
    Returns a dict with 'status' and 'div' keys suitable for the text field.
    """
    from zato_fhir.r4_0_1.narrative_templates import TEMPLATES
    
    resource_type = resource._resource_type
    
    if template is None:
        template_fields = TEMPLATES.get(resource_type, [])
        field_names = [f['name'] for f in template_fields]
        field_types = {f['name']: f['type'] for f in template_fields}
        field_is_list = {f['name']: f['is_list'] for f in template_fields}
        labels = {}
        custom_formatters = {}
    else:
        field_names = template.fields
        field_types = {}
        field_is_list = {}
        labels = template.labels
        custom_formatters = template.formatters
    
    lines = []
    obj_vars = vars(resource)
    
    for field_name in field_names:
        py_field_name = field_name + '_' if field_name in ('class', 'import', 'global', 'from') else field_name
        value = obj_vars.get(py_field_name)
        
        if value is None:
            continue
        
        label = labels.get(field_name) or to_label(field_name)
        field_type = field_types.get(field_name, 'string')
        is_list = field_is_list.get(field_name, False)
        
        if field_name in custom_formatters:
            formatted = custom_formatters[field_name](value)
        elif isinstance(value, list):
            formatted_items = [format_value(item, field_type) for item in value]
            formatted_items = [f for f in formatted_items if f]
            if not formatted_items:
                continue
            formatted = ', '.join(formatted_items)
        else:
            formatted = format_value(value, field_type)
        
        if not formatted:
            continue
        
        lines.append(f'<p><b>{escape(label)}:</b> {escape(formatted)}</p>')
    
    if not lines:
        lines.append(f'<p>{escape(resource_type)} resource</p>')
    
    div_content = '\n'.join(lines)
    div = f'<div xmlns="http://www.w3.org/1999/xhtml">\n{div_content}\n</div>'
    
    return {
        'status': 'generated',
        'div': div,
    }
