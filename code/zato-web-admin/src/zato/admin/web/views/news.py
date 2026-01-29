# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import configparser
from io import StringIO
from logging import getLogger

# requests
import requests

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed

logger = getLogger(__name__)

news_url = 'https://raw.githubusercontent.com/zatosource/zato-news/refs/heads/main/news.ini'

@method_allowed('GET')
def get_news(req):

    try:
        response = requests.get(news_url, timeout=10)
        response.raise_for_status()
        ini_content = response.text

        config = configparser.ConfigParser()
        config.read_string(ini_content)

        items = []
        for section in config.sections():
            item = {
                'date': section,
                'info': config.get(section, 'info', fallback=''),
                'gfx': config.get(section, 'gfx', fallback=''),
                'link': config.get(section, 'link', fallback='#'),
            }
            items.append(item)

        json_response = JsonResponse({'items': items})
        json_response['Cache-Control'] = 'public, max-age=86400'
        return json_response

    except Exception as e:
        logger.warning('Failed to fetch news: %s', e)
        return JsonResponse({'items': [], 'error': str(e)})
