# -*- coding: utf-8 -*-

"""
Dashboard creation views for monitoring wizards.
"""

# stdlib
import time
from logging import getLogger

# Django
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def dashboard_create_page(req):
    """Display the dashboard creation progress page."""

    # Get wizard parameters
    wizard_type_raw = req.GET.get('type', 'health')
    step1 = req.GET.get('step1', '')
    step2 = req.GET.get('step2', '')
    step3 = req.GET.get('step3', '')

    # Map wizard types to user-friendly names
    type_map = {
        'health': 'Health monitoring',
        'performance': 'Performance monitoring',
        'security': 'Security monitoring',
        'business': 'Business metrics'
    }

    # Map step2 values to readable text
    step2_map = {
        'current-status': 'Current status',
        'error-rate': 'Error rate',
        'uptime': 'Uptime',
        'activity': 'Activity'
    }

    # Map step3 values to readable text
    step3_map = {
        'real-time': 'Right now',
        'last-hour': 'Last hour',
        'last-day': 'Last day',
        'last-week': 'Last week',
        'last-month': 'Last month'
    }

    wizard_type = type_map.get(wizard_type_raw, wizard_type_raw.title())
    step2_text = step2_map.get(step2, step2)
    step3_text = step3_map.get(step3, step3)

    return render(req, 'zato/monitoring/dashboard/create.html', {
        'wizard_type': wizard_type,
        'step1': step1,
        'step2': step2,
        'step2_text': step2_text,
        'step3': step3,
        'step3_text': step3_text,
    })

# ################################################################################################################################

@csrf_exempt
@require_http_methods(['POST'])
def create_grafana_dashboard(req):
    """Create a Grafana dashboard."""

    # Sleep for testing purposes
    time.sleep(0.01)

    wizard_type = req.POST.get('type', '')
    step1 = req.POST.get('step1', '')
    step2 = req.POST.get('step2', '')
    step3 = req.POST.get('step3', '')

    logger.info(f'Creating Grafana dashboard: type={wizard_type}, step1={step1}, step2={step2}, step3={step3}')

    # Here would be the actual Grafana API calls
    # For now, just simulate success

    return JsonResponse({
        'success': True,
        'dashboard_id': 'grafana-123',
        'url': 'http://grafana.example.com/d/grafana-123'
    })

# ################################################################################################################################

@csrf_exempt
@require_http_methods(['POST'])
def create_datadog_dashboard(req):
    """Create a Datadog dashboard."""

    # Sleep for testing purposes
    time.sleep(0.01)

    wizard_type = req.POST.get('type', '')
    step1 = req.POST.get('step1', '')
    step2 = req.POST.get('step2', '')
    step3 = req.POST.get('step3', '')

    logger.info(f'Creating Datadog dashboard: type={wizard_type}, step1={step1}, step2={step2}, step3={step3}')

    # Here would be the actual Datadog API calls
    # For now, just simulate success

    return JsonResponse({
        'success': True,
        'dashboard_id': 'datadog-456',
        'url': 'https://app.datadoghq.com/dashboard/datadog-456'
    })

# ################################################################################################################################

@csrf_exempt
@require_http_methods(['POST'])
def try_service_code(req):
    """Try out the service code."""

    # Sleep for testing purposes
    time.sleep(3.3)

    logger.info('Service code invoked successfully')

    return JsonResponse({
        'success': True,
        'message': 'Service invoked successfully'
    })

# ################################################################################################################################
# ################################################################################################################################
