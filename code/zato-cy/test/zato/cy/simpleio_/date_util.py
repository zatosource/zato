# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

def parse_date(date_string):
    """ Parse a date string in a compatible way for Python 3.12 without using dateparser.
    """
    # Handle ISO date format YYYY-MM-DD
    if len(date_string) == 10 and date_string[4] == '-' and date_string[7] == '-':
        return datetime.strptime(date_string, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    # Handle ISO datetime format with Z (UTC timezone)
    elif 'Z' in date_string:
        # Strip the Z and any milliseconds
        clean_string = date_string.replace('Z', '+00:00')
        if '.' in clean_string:
            parts = clean_string.split('.')
            clean_string = parts[0] + '+00:00'
        return datetime.fromisoformat(clean_string)
    
    # Handle other ISO datetime formats
    elif 'T' in date_string:
        # Try to parse as ISO format
        try:
            return datetime.fromisoformat(date_string)
        except ValueError:
            # If there are milliseconds, try to handle that
            if '.' in date_string and '+' not in date_string and 'Z' not in date_string:
                base_date = date_string.split('.')[0]
                return datetime.fromisoformat(base_date).replace(tzinfo=timezone.utc)
            raise
    
    # Fall back to simple date parsing for anything else
    else:
        raise ValueError(f"Unsupported date format: {date_string}")
