from __future__ import annotations

from typing import Any


def get_extension(resource: Any, url: str) -> Any | None:
    """
    Get an extension value by URL from a FHIR resource or element.
    
    Args:
        resource: A FHIR resource or element with an 'extension' field
        url: The extension URL to find
    
    Returns:
        The extension value, or None if not found
    """
    extensions = _get_extensions(resource)
    if not extensions:
        return None
    
    for ext in extensions:
        if _get_url(ext) == url:
            return _get_value(ext)
    
    return None


def get_extensions(resource: Any, url: str) -> list[Any]:
    """
    Get all extension values matching a URL from a FHIR resource or element.
    
    Args:
        resource: A FHIR resource or element with an 'extension' field
        url: The extension URL to find
    
    Returns:
        List of extension values matching the URL
    """
    extensions = _get_extensions(resource)
    if not extensions:
        return []
    
    values = []
    for ext in extensions:
        if _get_url(ext) == url:
            value = _get_value(ext)
            if value is not None:
                values.append(value)
    
    return values


def has_extension(resource: Any, url: str) -> bool:
    """
    Check if a resource or element has an extension with the given URL.
    
    Args:
        resource: A FHIR resource or element with an 'extension' field
        url: The extension URL to check
    
    Returns:
        True if the extension exists, False otherwise
    """
    extensions = _get_extensions(resource)
    if not extensions:
        return False
    
    for ext in extensions:
        if _get_url(ext) == url:
            return True
    
    return False


def add_extension(resource: Any, url: str, value: Any, value_type: str = 'string') -> None:
    """
    Add an extension to a FHIR resource or element.
    
    Args:
        resource: A FHIR resource or element
        url: The extension URL
        value: The extension value
        value_type: The FHIR type of the value (string, boolean, integer, etc.)
    """
    ext = {
        'url': url,
        f'value{value_type.capitalize()}': value,
    }
    
    if isinstance(resource, dict):
        if 'extension' not in resource:
            resource['extension'] = []
        resource['extension'].append(ext)
    elif hasattr(resource, 'extension'):
        if resource.extension is None:
            resource.extension = []
        resource.extension.append(ext)


def remove_extension(resource: Any, url: str) -> bool:
    """
    Remove all extensions with the given URL from a resource or element.
    
    Args:
        resource: A FHIR resource or element
        url: The extension URL to remove
    
    Returns:
        True if any extensions were removed, False otherwise
    """
    extensions = _get_extensions(resource)
    if not extensions:
        return False
    
    original_len = len(extensions)
    new_extensions = [ext for ext in extensions if _get_url(ext) != url]
    
    if len(new_extensions) == original_len:
        return False
    
    if isinstance(resource, dict):
        resource['extension'] = new_extensions
    elif hasattr(resource, 'extension'):
        resource.extension = new_extensions
    
    return True


def get_nested_extension(resource: Any, *urls: str) -> Any | None:
    """
    Get a nested extension value by following a path of URLs.
    
    Args:
        resource: A FHIR resource or element
        *urls: The extension URLs to follow in order
    
    Returns:
        The nested extension value, or None if not found
    """
    if not urls:
        return None
    
    extensions = _get_extensions(resource)
    if not extensions:
        return None
    
    for ext in extensions:
        if _get_url(ext) != urls[0]:
            continue
        
        if len(urls) == 1:
            return _get_value(ext)
        
        nested = _get_nested_extensions(ext)
        if nested:
            for nested_ext in nested:
                result = get_nested_extension({'extension': [nested_ext]}, *urls[1:])
                if result is not None:
                    return result
    
    return None


def _get_extensions(obj: Any) -> list | None:
    """Get the extension list from an object."""
    if isinstance(obj, dict):
        return obj.get('extension')
    if hasattr(obj, 'extension'):
        return obj.extension
    return None


def _get_nested_extensions(ext: Any) -> list | None:
    """Get nested extensions from an extension."""
    if isinstance(ext, dict):
        return ext.get('extension')
    if hasattr(ext, 'extension'):
        return ext.extension
    return None


def _get_url(ext: Any) -> str | None:
    """Get the URL from an extension."""
    if isinstance(ext, dict):
        return ext.get('url')
    if hasattr(ext, 'url'):
        return ext.url
    return None


def _get_value(ext: Any) -> Any | None:
    """Get the value from an extension, checking all value[x] fields."""
    value_types = [
        'valueString', 'valueBoolean', 'valueInteger', 'valueDecimal',
        'valueUri', 'valueUrl', 'valueCanonical', 'valueCode',
        'valueDate', 'valueDateTime', 'valueTime', 'valueInstant',
        'valueBase64Binary', 'valueOid', 'valueId', 'valueMarkdown',
        'valueUnsignedInt', 'valuePositiveInt', 'valueUuid',
        'valueIdentifier', 'valueHumanName', 'valueAddress',
        'valueContactPoint', 'valueCoding', 'valueCodeableConcept',
        'valueQuantity', 'valueMoney', 'valueDuration', 'valueDistance',
        'valueCount', 'valueAge', 'valueRange', 'valueRatio',
        'valuePeriod', 'valueSampledData', 'valueSignature',
        'valueAttachment', 'valueReference', 'valueAnnotation',
    ]
    
    if isinstance(ext, dict):
        for vt in value_types:
            if vt in ext:
                return ext[vt]
        return None
    
    for vt in value_types:
        if hasattr(ext, vt):
            val = getattr(ext, vt)
            if val is not None:
                return val
    
    return None
