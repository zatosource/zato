<p align="center">
  <a href="https://zato.io"><img alt="" src="https://zato.io/static/img/intro/banner.webp" /></a>
</p>

# Zato /zɑːtəʊ/

ESB, SOA, API and Cloud Integrations in Python.

Zato is a Python-based, open-source platform that lets you automate, integrate and orchestrate business systems,
APIs, workflows as well as hardware assets in industries such as
[airports](https://zato.io/en/industry/airports/index.html),
[defense](https://zato.io/en/industry/defense/index.html),
[health care](https://zato.io/en/industry/healthcare/index.html),
[telecommunications](https://zato.io/en/industry/telecom/index.html),
financial services,
government
and more.

<p align="center">
  <a href="https://zato.io"><img alt="ESB, API Integrations and Automation in Python" src="https://upcdn.io/kW15bqq/raw/root/static/img/intro/bus.png" /></a>
</p>

## What does it look like in practice?

<p align="center">
<img src="https://github.com/user-attachments/assets/058b3ace-ddc3-47a3-b803-302122419aba" alt="" width="600"/>
</p>

```python
# Zato
from zato.server.service import Service

class SampleServiceREST(Service):

    def handle(self):

        # Request to send ..
        request = {'user_id':123, 'balance':1357, 'currency':'USD'}

        # .. get a connection to our previously created REST endpoint ..
        conn = self.out.rest['Billing'].conn

        # .. invoke it ..
        response = conn.post(self.cid, request)

        # .. and return the response to our caller.
        self.response.payload = response.data
```

## Learn more

Visit https://zato.io for the details, including:

* [Downloads](https://zato.io/en/docs/3.2/admin/guide/install/index.html)
* [Screenshots](https://zato.io/en/docs/3.2/intro/screenshots.html)
* [Programming examples](https://zato.io/en/docs/3.2/dev/index.html)
