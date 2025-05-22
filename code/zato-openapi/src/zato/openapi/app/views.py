# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import json
import logging
from pathlib import Path

# Django
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

# PyYAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@require_GET
def openapi_spec(request):
    """ Serves the OpenAPI specification as JSON.
    """
    try:
        # Get the OpenAPI spec path from environment or use default
        spec_path = settings.OPENAPI_SPEC_PATH

        # Check if the file exists
        if not Path(spec_path).exists():
            logger.warning(f'OpenAPI spec file not found at {spec_path}')
            return JsonResponse({'error': 'OpenAPI specification file not found'}, status=404)

        # Load the YAML file directly as text
        with open(spec_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()

        # Parse the YAML content
        spec_yaml = yaml.safe_load(yaml_content)

        paths_data = spec_yaml.get('paths')

        if not paths_data:
            error_message = 'OpenAPI spec is missing \'paths\' section, or the \'paths\' section is null or empty.'
            logger.error(f'{error_message} Spec keys found: {list(spec_yaml.keys())}')
            return JsonResponse({'error': error_message, 'openapi_spec_keys': list(spec_yaml.keys())}, status=400)

        if not isinstance(paths_data, dict):
            error_message = f'OpenAPI spec \'paths\' section is not a dictionary (type found: {type(paths_data).__name__}).'
            logger.error(f'{error_message} Spec keys found: {list(spec_yaml.keys())}')
            return JsonResponse({'error': error_message, 'openapi_spec_keys': list(spec_yaml.keys())}, status=400)

        if not paths_data: # Handles paths: {} which is an empty dictionary
            error_message = 'OpenAPI spec \'paths\' section is an empty dictionary.'
            logger.error(f'{error_message} Spec keys found: {list(spec_yaml.keys())}')
            return JsonResponse({'error': error_message, 'openapi_spec_keys': list(spec_yaml.keys())}, status=400)

        # Verify all required sections are present
        required_sections = ['openapi', 'info', 'paths', 'components']
        for section in required_sections:
            if section not in spec_yaml:
                logger.warning(f'Missing {section} section in OpenAPI specification')

        # Log the structure of the spec for debugging
        logger.info(f'OpenAPI spec sections: {list(spec_yaml.keys())}')
        logger.info(f'Number of paths: {len(paths_data)} paths found')

        json_content = json.dumps(spec_yaml)
        return HttpResponse(json_content, content_type='application/json')

    except Exception as e:
        logger.error(f'Error serving OpenAPI spec: {e}')
        return JsonResponse({'error': 'Error processing OpenAPI specification'}, status=500)

# ################################################################################################################################

@require_GET
def swagger_ui(request):
    """ Serves the Swagger UI page.
    """
    return render(request, 'swagger.html')

# ################################################################################################################################
# ################################################################################################################################
