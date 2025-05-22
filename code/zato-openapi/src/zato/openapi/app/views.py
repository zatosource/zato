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
        
        # Load the YAML file
        with open(spec_path, 'r') as f:
            spec_yaml = yaml.safe_load(f)
        
        # Return as JSON
        return JsonResponse(spec_yaml)
    
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
