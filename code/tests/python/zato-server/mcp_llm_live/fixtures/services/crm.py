# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the directory the invocation marker file lives in -
# the test suite sets it for the server process and reads the file to prove
# whether a service did or did not run.
_marker_dir_env_key = 'Zato_Test_LLM_Marker_Dir'

# The file each service invocation appends its name to
_marker_file_name = 'invocations.txt'

# The file the order status service appends each payload it received to
_payload_file_name = 'payloads.txt'

# The customer the CRM answers about
_customer_id = 'CRM-1001'

# The order id the status service answers for and the one the cancel service refuses
_order_id                 = 'ORD-7002'
_order_id_not_cancellable = 'ORD-7003'

# A base64 blob long enough for the base64 stripping stage to recognize it as one
_avatar_blob = 'data:image/png;base64,' + 'QUJDREVG' * 40

# A base64-looking string below the stripping stage's length floor - it always survives
_thumb_blob = 'data:image/png;base64,QUJDREVG'

# One Japanese sentence of the history record, repeated and joined with ideographic
# spaces so a truncation boundary always lands between whole sentences
_history_sentence = '東京の顧客担当チームは請求書の確認と発送状況の連絡を毎営業日に行います'
_history_repeat = 700
_history_separator = '\u3000'

# The reaction tokens of the emoji record - an astral-plane emoji, a skin-tone pair,
# a joiner sequence, Greek diacritics and a decomposed combining sequence -
# repeated until the record is long enough for the size cap to cut it
_reaction_tokens = ('🚀', '👍🏽', '🧑\u200d💻', 'γειά', 'καφε\u0301δες')
_reaction_repeat = 1200

# The credential-shaped values of the secrets record - one value per detector of the secrets
# removal stage, the AWS key written twice in one field for the stable-replacement assertions.
_secret_api_token   = 'sk-crm9001integration0abc'
_secret_aws_key     = 'AKIA2E74XAMPLE9001AB'
_secret_jwt         = 'eyJhbGciOiJIUzI1NiJ9.eyJjcm0iOiI5MDAxIn0.c2lnbmF0dXJlOTAwMQ'
_secret_bearer      = 'Bearer crm9001tokenvalue77'
_secret_conn_string = 'postgres://reporting:Zx9001pass@db.internal:5432/crm'

_secret_private_key = (
    '-----BEGIN RSA PRIVATE KEY-----\n'
    'MIIEowIBAAKCAQEAcrm9001exampleline1\n'
    'MIIEowIBAAKCAQEAcrm9001exampleline2\n'
    '-----END RSA PRIVATE KEY-----')

# The customers beyond the main one - a Greek record whose contacts line carries two distinct
# emails, a Japanese record with PII nested in objects and arrays plus a national id only
# the jp land's detectors recognize, a diacritics record with PII inside Greek prose,
# a Hebrew record with clean and padded text, a mixed-script record whose fields
# exercise every pipeline stage at once, a Japanese history long enough to cross the size
# cap, an emoji record for the truncation boundary and a record whose notes carry
# credential-shaped values for the secrets removal stage.
_extra_customers = {
    'CRM-2001': {
        'name': 'Νίκος Παπαδόπουλος',
        'city': 'Αθήνα',
        'email': 'nikos.papadopoulos@example.com',
        'contacts': 'primary nikos.papadopoulos@example.com backup n.papadopoulos@example.org',
    },
    'CRM-3001': {
        'name': '山田太郎',
        'city': '東京',
        'email': 'taro.yamada@example.com',
        'national_id': '123456789018',
        'profile': {
            'emails': ['taro.yamada@example.com'],
            'device': {'imei': '490154203237518'},
        },
    },
    'CRM-4001': {
        'name': 'Αντιγόνη Χατζή',
        'city': 'Ηράκλειο',
        'notes_support': 'Ώρες εξυπηρέτησης καθημερινά, γράψτε στο antigoni.chatzi@example.com το απόγευμα',
        'notes_billing': 'Μεγαλύτερες αλλαγές θέλουν έγκριση, στείλτε στο thalia.oikonomou@example.com ευχαριστώ πολύ',
    },
    'CRM-5001': {
        'name': 'דוד לוי',
        'city': 'תל אביב',
        'greeting': 'שלום וברכה מצוות שירות הלקוחות',
        'notes': 'לקוח   ותיק    נאמן',
    },
    'CRM-6001': {
        'name': 'Θεοδώρα Μακρή-Ζαφείρη',
        'city': 'Αθήνα',
        'motto': '顧客第一 שלום וברכה καλή τύχη 🚀 👍🏽',
        'fax': None,
        'note': 'Καλή    τύχη   φίλε',
        'email': 'theodora.makri@example.com',
        'banner': '<script>showBanner()</script>Ωμέγα δράση',
        'links': 'see https://example.com/kb and https://tracking.invalid/kb',
        'attachment': _avatar_blob,
    },
    'CRM-7001': {
        'name': '佐藤花子',
        'city': '大阪',
        'history': _history_separator.join([_history_sentence] * _history_repeat),
    },
    'CRM-8001': {
        'name': 'Renata Brixen',
        'city': 'Innsbruck',
        'reactions': ' '.join(list(_reaction_tokens) * _reaction_repeat),
    },
    'CRM-9001': {
        'name': 'Ines Kaltenbrunner',
        'city': 'Salzburg',
        'api_note': f'The integration was provisioned with {_secret_api_token} last spring',
        'aws_note': f'Backups sign with {_secret_aws_key}, the standby job reuses {_secret_aws_key} as well',
        'session_note': f'The portal session cookie carries {_secret_jwt}',
        'auth_note': f'Each call sends Authorization: {_secret_bearer}',
        'db_note': f'Reports read from {_secret_conn_string} nightly',
        'deploy_key': _secret_private_key,
    },
}

# ################################################################################################################################
# ################################################################################################################################

def _record_invocation(service_name:'str') -> 'None':
    """ Appends the service's name to the marker file the test suite reads,
    which is how tests prove a service was or was not invoked.
    """
    marker_dir = os.environ.get(_marker_dir_env_key)

    if not marker_dir:
        return

    marker_path = os.path.join(marker_dir, _marker_file_name)

    with open(marker_path, 'a') as marker_file:
        _ = marker_file.write(service_name + '\n')

# ################################################################################################################################

def _record_payload(service_name:'str', payload:'object') -> 'None':
    """ Appends the payload a service received to the payload marker file,
    which is how tests prove exactly what did and did not reach a service.
    """
    marker_dir = os.environ.get(_marker_dir_env_key)

    if not marker_dir:
        return

    payload_path = os.path.join(marker_dir, _payload_file_name)

    with open(payload_path, 'a') as payload_file:
        _ = payload_file.write(f'{service_name} {payload!r}\n')

# ################################################################################################################################
# ################################################################################################################################

class CustomerGet(Service):
    """ Returns the full CRM record of a customer - contact details, devices and account notes.
    """

    name = 'crm.customer.get'
    input = 'customer_id'

    def handle(self):

        _record_invocation(self.name)

        customer_id = self.request.input.customer_id

        # The extra customers carry the non-ASCII names and the nested PII of their tests ..
        if extra_customer := _extra_customers.get(customer_id):

            record:'anydict' = dict(extra_customer)
            record['customer_id'] = customer_id
            record['found'] = True

            self.response.payload = record
            return

        # .. an unknown customer is an empty record, the known one is the full CRM document
        # whose fields exercise every safeguard stage - one email, three valid IMEIs in mixed
        # written forms plus one with a broken checksum, a twice-repeated IPv4 address,
        # null fields at the top level and nested, a null array element, a base64 blob with
        # a short base64-looking thumb next to it, markup, URLs on and off the allow list
        # including a subdomain and a lookalike host, a zero-width space and decomposed Unicode.
        if customer_id != _customer_id:
            self.response.payload = {'customer_id': customer_id, 'found': False}
            return

        self.response.payload = {
            'customer_id': _customer_id,
            'found': True,
            'name': 'Renata Brixen',
            'city': 'Innsbruck',
            'email': 'renata.brixen@example.com',
            'fax': None,
            'secondary_email': None,
            'tags': ['vip', None, 'beta'],
            'billing': {'iban': None, 'plan': 'monthly'},
            'devices': [
                {'label': 'phone-main',   'imei': '490154203237518'},
                {'label': 'phone-backup', 'imei': '35-209900-176148-1'},
                {'label': 'tablet',       'imei': '86 723902 235411 8'},
                {'label': 'retired',      'imei': '490154203237519'},
            ],
            'network': 'primary 203.0.113.77 standby 203.0.113.77 gateway 198.51.100.9',
            'notes': (
                'Alpha    Beta  <script>showBanner()</script> account of Mu\u0308ller CRM\u200bID '
                'see https://example.com/crm/docs and https://tracking.invalid/pixel '
                'more at https://api.example.com/kb and https://notexample.com/kb'),
            'avatar': _avatar_blob,
            'thumb': _thumb_blob,
        }

# ################################################################################################################################
# ################################################################################################################################

class InvoiceList(Service):
    """ Lists a customer's invoices - pass how many of the most recent invoices to return.
    """

    name = 'crm.invoice.list'
    input = 'count'

    def handle(self):

        _record_invocation(self.name)

        count = int(self.request.input.count)

        invoices = []

        for index in range(count):
            number = index + 1
            invoices.append({
                'invoice_id': f'INV-2026-{number:04d}',
                'customer_id': _customer_id,
                'total': 100 + number,
                'currency': 'EUR',
                'notes': f'Invoice {number} of {count}, monthly CRM subscription and support hours',
            })

        self.response.payload = {'count': count, 'invoices': invoices}

# ################################################################################################################################
# ################################################################################################################################

class OrderStatus(Service):
    """ Reports the delivery status of an order - pass the order id to check.
    """

    name = 'crm.order.status'
    input = 'order_id'

    def handle(self):

        _record_invocation(self.name)
        _record_payload(self.name, self.request.raw_request)

        order_id = self.request.input.order_id

        self.response.payload = {
            'order_id': order_id,
            'status': 'shipped',
            'carrier': 'DHL',
            'eta_days': 3,
        }

# ################################################################################################################################
# ################################################################################################################################

class OrderCancel(Service):
    """ Cancels an order - pass the order id to cancel.
    """

    name = 'crm.order.cancel'
    input = 'order_id'

    def handle(self):

        _record_invocation(self.name)

        order_id = self.request.input.order_id

        # This order is beyond cancellation and trying is an error the gateway must report
        if order_id == _order_id_not_cancellable:
            raise Exception(f'Order `{order_id}` cannot be cancelled')

        self.response.payload = {
            'order_id': order_id,
            'status': 'cancelled',
        }

# ################################################################################################################################
# ################################################################################################################################
