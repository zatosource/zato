import requests
import base64
import json


input = {'service_request': 'hola'}

payload = {
    'name': 'test-service.test-service',
    'data_format': 'json',
    'channel': 'http-soap',
    'payload': base64.b64encode(json.dumps(input))}

r = requests.post('http://uiraider.dv:11223/zato/json/zato.service.invoke', data=json.dumps(payload), auth=('pubapi', '123'))

zato_response = r.json()
service_response_b64 = zato_response.get('zato_service_invoke_response').get('response')
service_response = base64.b64decode(service_response_b64)
print (service_response)