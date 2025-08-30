# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import os
import re
import sys

def postprocess_k6_script():
    script_path = sys.argv[1]
    
    # Read environment variables
    username = os.environ.get('Zato_Test_PubSub_OpenAPI_Username')
    password = os.environ.get('Zato_Test_PubSub_OpenAPI_Password')
    
    if not username or not password:
        raise ValueError('Zato_Test_PubSub_OpenAPI_Username and Zato_Test_PubSub_OpenAPI_Password environment variables must be set')
    
    # Create Basic Auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Read the generated script
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Replace base URL
    content = content.replace('<BASE_URL>', 'http://localhost:44556')
    
    # Add authentication to client initialization
    client_pattern = r'(const \w+Client = new \w+Client\(\{ baseUrl \}\))'
    auth_replacement = r'\1\n  // Add authentication headers\n  \1.defaults = { headers: { Authorization: "' + auth_header + '" } };'
    content = re.sub(client_pattern, auth_replacement, content)
    
    # Fix invalid test data
    content = re.sub(r'priority: \d{10,}', 'priority: 5', content)
    content = re.sub(r'expiration: \d{10,}', 'expiration: 3600', content)
    content = re.sub(r'pub_time: "[^"]*"', 'pub_time: "2025-01-01T12:00:00+00:00"', content)
    
    # Write back the processed script
    with open(script_path, 'w') as f:
        f.write(content)

if __name__ == '__main__':
    postprocess_k6_script()
