# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from base64 import b64encode
from hashlib import sha256

# Zato
from documents import get_document_mix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The approximate size of each kind of document, in bytes.
Admission_Size      = 2_000
EDIFACT_Order_Size  = 30_000
FHIR_Bundle_Size    = 250_000
Ship_Notice_Size    = 300_000
PDF_Envelope_Sizes  = (3_000_000, 10_000_000)

# How many documents of each kind one cycle of the production mix holds, in addition to the documents of the base mix.
_admission_count     = 6
_edifact_order_count = 4
_fhir_bundle_count   = 2
_ship_notice_count   = 2

# The trading partners, with the non-ASCII characters of their registered names.
_partners = [
    ('5790000000012', 'Société Générale de Fournitures SA', 'Paris', 'FR'),
    ('4012345000009', 'Müller Logistik GmbH', 'Düsseldorf', 'DE'),
    ('5901234000007', 'Łódzkie Zakłady Dystrybucji Sp. z o.o.', 'Łódź', 'PL'),
    ('7350012340008', 'Ångström Medicinteknik AB', 'Göteborg', 'SE'),
    ('8412345000005', 'Distribuciones Peña y Núñez S.L.', 'Logroño', 'ES'),
]

# The patients of the clinical documents - family name, given name, sex, date of birth, street, city, postal code, country.
_patients = [
    ('MÜLLER', 'JÜRGEN', 'M', '19750314', 'Königsallee 1', 'Düsseldorf', '40212', 'DE'),
    ('ŁUKASIEWICZ', 'ZOFIA', 'F', '19820627', 'ul. Piotrkowska 104', 'Łódź', '90-926', 'PL'),
    ('GARCÍA NÚÑEZ', 'JOSÉ', 'M', '19691102', 'Calle Mayor 12', 'Logroño', '26001', 'ES'),
    ('LEFÈVRE', 'HÉLÈNE', 'F', '19880919', '12 Rue de Rivoli', 'Paris', '75001', 'FR'),
    ('ÅKESSON', 'BJÖRN', 'M', '19540105', 'Kungsportsavenyen 3', 'Göteborg', '41136', 'SE'),
]

# The products of the orders and shipments - name, unit price in cents.
_products = [
    ('Industrial bearing 6204-2RS', 412),
    ('Hydraulic hose 1/2 in, 10 m', 3890),
    ('Stainless hex bolt M10x40', 37),
    ('Nitrile gloves, box of 100', 1150),
    ('Safety goggles, anti-fog', 860),
    ('Cable tie 300 mm, pack of 100', 520),
    ('Pallet wrap film 500 mm', 2475),
    ('Thermal label roll 100x150', 1890),
]

# The vital signs of the admissions and of the clinical bundles - LOINC code, name, unit, base value.
_vital_signs = [
    ('8867-4', 'Heart rate', '/min', 72),
    ('8480-6', 'Systolic blood pressure', 'mm[Hg]', 124),
    ('8462-4', 'Diastolic blood pressure', 'mm[Hg]', 81),
    ('8310-5', 'Body temperature', 'Cel', 37),
    ('9279-1', 'Respiratory rate', '/min', 16),
    ('59408-5', 'Oxygen saturation', '%', 97),
]

# The page layout of the generated invoices, in points.
_pdf_page_width = 595
_pdf_page_height = 842
_pdf_lines_per_page = 70
_pdf_leading = 11

# ################################################################################################################################
# ################################################################################################################################

def _gtin(number:'int') -> 'str':
    """ A GTIN-13 of the given item number, with its check digit.
    """
    digits = f'590123{number:06d}'
    total = 0

    for position, digit in enumerate(digits):
        weight = 3 if position % 2 else 1
        total += int(digit) * weight

    check_digit = (10 - total % 10) % 10

    out = f'{digits}{check_digit}'
    return out

# ################################################################################################################################

def _uuid(*parts:'object') -> 'str':
    """ A stable identifier in the form of a UUID, derived from the given parts.
    """
    seed = '/'.join(map(str, parts))
    digest = sha256(seed.encode('utf8')).hexdigest()

    out = f'{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}'
    return out

# ################################################################################################################################

def _new_admission(index:'int') -> 'str':
    """ An HL7 v2.5.1 ADT^A01 message admitting a patient, in UTF-8.
    """
    family, given, sex, birth_date, street, city, postal_code, country = _patients[index % len(_patients)]

    segments:'strlist' = [
        f'MSH|^~\\&|ADT|ACME_HOSPITAL|EHR|ACME_HOSPITAL|20261031101500||ADT^A01^ADT_A01|ADT{index:010d}|P|2.5.1|||AL|NE||UNICODE UTF-8',
        'EVN|A01|20261031101500',
        f'PID|1||PAT{index:08d}^^^ACME^MR||{family}^{given}^^^^^L||{birth_date}|{sex}|||{street}^^{city}^^{postal_code}^{country}',
        f'NK1|1|{family}^ANNA|SPO|{street}^^{city}^^{postal_code}^{country}|+49 211 5550100',
        f'PV1|1|I|CARD^0412^B^ACME||||1234^ŁUKASIEWICZ^ZOFIA^^^DR|||CAR||||1|||1234^ŁUKASIEWICZ^ZOFIA^^^DR|IP|VIS{index:08d}',
        'PV2|||^Chest pain on exertion',
        'AL1|1|DA|^Penicillin|SV|Anaphylaxis',
        'DG1|1||I20.9^Angina pectoris, unspecified^I10|||A',
        f'IN1|1|PLAN01|INS001|Allgemeine Ortskrankenkasse Rheinland|Kasernenstraße 61^^Düsseldorf^^40213^DE|||||||||||{family}^{given}',
    ]

    total_size = 0

    for segment in segments:
        total_size += len(segment.encode('utf8')) + 1

    observation_index = 0

    # The vital signs are recorded until the message reaches its size.
    while total_size < Admission_Size:

        code, name, unit, base_value = _vital_signs[observation_index % len(_vital_signs)]
        value = base_value + observation_index % 3
        set_id = observation_index + 1

        segment = f'OBX|{set_id}|NM|{code}^{name}^LN||{value}|{unit}|||||F|||20261031101000'
        segments.append(segment)

        total_size += len(segment.encode('utf8')) + 1
        observation_index += 1

    out = '\r'.join(segments)
    return out

# ################################################################################################################################

def _edifact_text(value:'str') -> 'str':
    """ Escapes the service characters of EDIFACT in a text element with the release character.
    """
    out = value.replace('?', '??')
    out = out.replace('+', '?+')
    out = out.replace(':', '?:')
    out = out.replace("'", "?'")

    return out

# ################################################################################################################################

def _new_edifact_order(index:'int') -> 'str':
    """ An EDIFACT ORDERS D.96A message in the UNOC character set, between two of the trading partners.
    """
    buyer_gln, buyer_name, buyer_city, buyer_country = _partners[index % len(_partners)]
    seller_gln, seller_name, seller_city, seller_country = _partners[(index + 1) % len(_partners)]

    segments:'strlist' = [
        'UNH+1+ORDERS:D:96A:UN:EAN008',
        f'BGM+220+PO{index:010d}+9',
        'DTM+137:20261031:102',
        f'NAD+BY+{buyer_gln}::9++{_edifact_text(buyer_name)}+++{_edifact_text(buyer_city)}++{buyer_country}',
        f'NAD+SU+{seller_gln}::9++{_edifact_text(seller_name)}+++{_edifact_text(seller_city)}++{seller_country}',
        'CUX+2:EUR:9',
    ]

    header = f"UNA:+.? 'UNB+UNOC:3+{buyer_gln}:14+{seller_gln}:14+261031:1015+{index:014d}'\n"
    total_size = len(header.encode('utf8'))

    for segment in segments:
        total_size += len(segment.encode('utf8')) + 2

    line_index = 0

    # Order lines are added until the message reaches its size ..
    while total_size < EDIFACT_Order_Size:

        product_index = line_index % len(_products)
        description, price_cents = _products[product_index]
        line_number = line_index + 1

        line_segments = [
            f'LIN+{line_number}++{_gtin(product_index + 1)}:EN',
            f'PIA+1+SKU{product_index + 1:06d}:SA',
            f'IMD+F++:::{_edifact_text(description)}',
            f'QTY+21:{line_index % 40 + 1}',
            f'PRI+AAA:{price_cents / 100:.2f}',
        ]

        for segment in line_segments:
            segments.append(segment)
            total_size += len(segment.encode('utf8')) + 2

        line_index += 1

    # .. and the trailers close the message, counting its segments, and the interchange.
    segments.append('UNS+S')
    segments.append(f'CNT+2:{line_index}')

    segment_count = len(segments) + 1
    segments.append(f'UNT+{segment_count}+1')

    body = "'\n".join(segments)

    out = f"{header}{body}'\nUNZ+1+{index:014d}'\n"
    return out

# ################################################################################################################################

def _new_ship_notice(index:'int') -> 'str':
    """ An X12 856 advance ship notice of one shipment, with its orders, packs and items.
    """
    sender = 'ACMESUPPLIER'.ljust(15)
    receiver = 'ACMEBUYER'.ljust(15)
    empty_field = ' ' * 10

    envelope:'strlist' = [
        f'ISA*00*{empty_field}*00*{empty_field}*ZZ*{sender}*ZZ*{receiver}*261031*1015*U*00401*{index:09d}*0*P*>',
        f'GS*SH*ACMESUPPLIER*ACMEBUYER*20261031*1015*{index}*X*004010',
    ]

    segments:'strlist' = [
        'ST*856*0001',
        f'BSN*00*SHP{index:010d}*20261031*1015*0001',
        'HL*1**S',
        'TD1*CTN25*120****G*1450*LB',
        'TD5*B*2*ACMF*M*ACME FREIGHT',
        f'REF*BM*BOL{index:010d}',
        'DTM*011*20261031',
        'N1*ST*ACME STORE 0042*92*000042',
        'N1*SF*ACME INDUSTRIAL SUPPLY*92*000001',
    ]

    total_size = 0

    for segment in envelope + segments:
        total_size += len(segment) + 1

    hl_number = 1
    order_index = 0

    # Orders with their packs and items are added until the notice reaches its size ..
    while total_size < Ship_Notice_Size:

        hl_number += 1
        order_hl = hl_number
        order_segments = [f'HL*{order_hl}*1*O', f'PRF*PO{index * 1000 + order_index:010d}***20261029']

        for pack_index in range(4):

            hl_number += 1
            pack_hl = hl_number
            serial = index * 100_000 + order_index * 10 + pack_index
            order_segments.append(f'HL*{pack_hl}*{order_hl}*P')
            order_segments.append(f'MAN*GM*00{_gtin(serial % 1_000_000)}{serial:05d}')

            for item_index in range(6):

                hl_number += 1
                product_index = (order_index + item_index) % len(_products)
                description, _ignored_price = _products[product_index]

                order_segments.append(f'HL*{hl_number}*{pack_hl}*I')
                order_segments.append(f'LIN**VP*SKU{product_index + 1:06d}*EN*{_gtin(product_index + 1)}')
                order_segments.append(f'SN1**{item_index % 12 + 1}*EA')
                order_segments.append(f'PID*F****{description.upper()}')

        for segment in order_segments:
            segments.append(segment)
            total_size += len(segment) + 1

        order_index += 1

    # .. and the trailers close the transaction set, the group and the interchange.
    segments.append(f'CTT*{hl_number}')

    segment_count = len(segments) + 1
    segments.append(f'SE*{segment_count}*0001')

    trailer = [f'GE*1*{index}', f'IEA*1*{index:09d}']

    out = '~'.join(envelope + segments + trailer)
    out += '~'

    return out

# ################################################################################################################################

def _new_fhir_bundle(index:'int') -> 'str':
    """ A FHIR R4 transaction Bundle with a patient, an encounter and the observations recorded during it.
    """
    family, given, sex, birth_date, street, city, postal_code, country = _patients[index % len(_patients)]

    patient_url = f'urn:uuid:{_uuid("patient", index)}'
    encounter_url = f'urn:uuid:{_uuid("encounter", index)}'

    gender = 'male' if sex == 'M' else 'female'
    birth_date_iso = f'{birth_date[:4]}-{birth_date[4:6]}-{birth_date[6:]}'

    entries:'anylist' = [
        {
            'fullUrl': patient_url,
            'resource': {
                'resourceType': 'Patient',
                'identifier': [{'system': 'urn:oid:1.2.3.4.5.6', 'value': f'PAT{index:08d}'}],
                'name': [{'family': family.title(), 'given': [given.title()]}],
                'gender': gender,
                'birthDate': birth_date_iso,
                'address': [{'line': [street], 'city': city, 'postalCode': postal_code, 'country': country}],
            },
            'request': {'method': 'POST', 'url': 'Patient'},
        },
        {
            'fullUrl': encounter_url,
            'resource': {
                'resourceType': 'Encounter',
                'status': 'finished',
                'class': {'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode', 'code': 'IMP'},
                'subject': {'reference': patient_url},
                'period': {'start': '2026-10-29T08:00:00+01:00', 'end': '2026-10-31T10:00:00+01:00'},
            },
            'request': {'method': 'POST', 'url': 'Encounter'},
        },
    ]

    bundle:'anydict' = {
        'resourceType': 'Bundle',
        'id': _uuid('bundle', index),
        'type': 'transaction',
        'entry': entries,
    }

    total_size = len(json.dumps(bundle, ensure_ascii=False).encode('utf8'))
    observation_index = 0

    # The vital signs taken every hour of the stay are added until the bundle reaches its size.
    while total_size < FHIR_Bundle_Size:

        code, name, unit, base_value = _vital_signs[observation_index % len(_vital_signs)]
        hour = observation_index // len(_vital_signs)

        entry = {
            'fullUrl': f'urn:uuid:{_uuid("observation", index, observation_index)}',
            'resource': {
                'resourceType': 'Observation',
                'status': 'final',
                'category': [{'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/observation-category', 'code': 'vital-signs'}]}],
                'code': {'coding': [{'system': 'http://loinc.org', 'code': code, 'display': name}]},
                'subject': {'reference': patient_url},
                'encounter': {'reference': encounter_url},
                'effectiveDateTime': f'2026-10-{29 + hour // 24 % 3:02d}T{hour % 24:02d}:00:00+01:00',
                'valueQuantity': {'value': base_value + observation_index % 3, 'unit': unit,
                    'system': 'http://unitsofmeasure.org', 'code': unit},
            },
            'request': {'method': 'POST', 'url': 'Observation'},
        }

        entries.append(entry)
        total_size += len(json.dumps(entry, ensure_ascii=False).encode('utf8')) + 2
        observation_index += 1

    out = json.dumps(bundle, ensure_ascii=False)
    return out

# ################################################################################################################################

def _pdf_text(value:'str') -> 'str':
    """ Escapes the characters of a PDF literal string.
    """
    out = value.replace('\\', '\\\\')
    out = out.replace('(', '\\(')
    out = out.replace(')', '\\)')

    return out

# ################################################################################################################################

def _new_invoice_pdf(index:'int', target_size:'int') -> 'bytes':
    """ A PDF invoice whose pages list the invoice lines in Helvetica, as many pages as the target size requires.
    """
    font = b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>'
    contents:'anylist' = []
    total_size = 0
    line_number = 0

    # Pages of invoice lines are added until the document reaches its size ..
    while total_size < target_size:

        lines:'strlist' = [f'BT /F1 9 Tf {_pdf_leading} TL 40 {_pdf_page_height - 40} Td']

        for _ignored in range(_pdf_lines_per_page):

            line_number += 1
            product_index = line_number % len(_products)
            description, price_cents = _products[product_index]
            quantity = line_number % 40 + 1
            total_cents = quantity * price_cents

            text = f'{line_number:7d}  SKU-{product_index + 1:06d}  {description:<32} {quantity:>4} x ' + \
                f'{price_cents / 100:>9.2f} EUR = {total_cents / 100:>11.2f} EUR'

            lines.append(f'({_pdf_text(text)}) Tj T*')

        lines.append('ET')

        stream = '\n'.join(lines).encode('latin-1')
        contents.append(stream)

        total_size += len(stream) + 200

    # .. and the objects are written with the cross-reference table that locates each of them.
    page_count = len(contents)
    kids:'strlist' = []

    for page_index in range(page_count):
        kids.append(f'{4 + page_index * 2} 0 R')

    objects:'list[bytes]' = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {page_count} >>'.encode('ascii'),
        font,
    ]

    for page_index, stream in enumerate(contents):
        content_number = 5 + page_index * 2
        page = f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_pdf_page_width} {_pdf_page_height}] ' + \
            f'/Resources << /Font << /F1 3 0 R >> >> /Contents {content_number} 0 R >>'
        objects.append(page.encode('ascii'))
        objects.append(b'<< /Length ' + str(len(stream)).encode('ascii') + b' >>\nstream\n' + stream + b'\nendstream')

    parts:'list[bytes]' = [b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n']
    offsets:'intlist' = []
    position = len(parts[0])

    for object_index, body in enumerate(objects):
        offsets.append(position)
        part = f'{object_index + 1} 0 obj\n'.encode('ascii') + body + b'\nendobj\n'
        parts.append(part)
        position += len(part)

    xref_lines = [f'xref\n0 {len(objects) + 1}\n', '0000000000 65535 f \n']

    for offset in offsets:
        xref_lines.append(f'{offset:010d} 00000 n \n')

    trailer = f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /ID [<{_uuid("invoice", index).replace("-", "")}>' + \
        f'<{_uuid("invoice", index).replace("-", "")}>] >>\nstartxref\n{position}\n%%EOF\n'

    parts.append(''.join(xref_lines).encode('ascii'))
    parts.append(trailer.encode('ascii'))

    out = b''.join(parts)
    return out

# ################################################################################################################################

def _new_pdf_envelope(index:'int', size:'int') -> 'str':
    """ A JSON envelope of an invoice sent to a trading partner, with the PDF of the invoice in base64.
    """
    gln, partner_name, city, country = _partners[index % len(_partners)]

    # Base64 makes the PDF a third larger, so the PDF is three quarters of the envelope.
    pdf = _new_invoice_pdf(index, size * 3 // 4)

    envelope = {
        'type': 'invoice_document',
        'invoice_number': f'INV-2026-{index:08d}',
        'recipient': {'gln': gln, 'name': partner_name, 'city': city, 'country': country},
        'content_type': 'application/pdf',
        'file_name': f'Rechnung_{index:08d}_{city}.pdf',
        'sha256': sha256(pdf).hexdigest(),
        'size': len(pdf),
        'content': b64encode(pdf).decode('ascii'),
    }

    out = json.dumps(envelope, ensure_ascii=False)
    return out

# ################################################################################################################################

def get_production_documents() -> 'strlist':
    """ One cycle of the production mix - the base mix of receipts, lab results, purchase orders and X12 850 batches,
    together with HL7 admissions, EDIFACT orders, FHIR bundles, X12 856 ship notices and PDF invoices of 3 and 10 MB,
    sized from 1 KB to 10 MB with most documents small and few large, interleaved so that each part of the cycle
    carries documents of each size.
    """
    kinds:'list[strlist]' = []

    kinds.append(get_document_mix())

    admissions:'strlist' = []
    for index in range(_admission_count):
        admissions.append(_new_admission(index))
    kinds.append(admissions)

    edifact_orders:'strlist' = []
    for index in range(_edifact_order_count):
        edifact_orders.append(_new_edifact_order(index))
    kinds.append(edifact_orders)

    fhir_bundles:'strlist' = []
    for index in range(_fhir_bundle_count):
        fhir_bundles.append(_new_fhir_bundle(index))
    kinds.append(fhir_bundles)

    ship_notices:'strlist' = []
    for index in range(_ship_notice_count):
        ship_notices.append(_new_ship_notice(index))
    kinds.append(ship_notices)

    pdf_envelopes:'strlist' = []
    for index, size in enumerate(PDF_Envelope_Sizes):
        pdf_envelopes.append(_new_pdf_envelope(index, size))
    kinds.append(pdf_envelopes)

    document_count = 0
    for kind in kinds:
        document_count += len(kind)

    out:'strlist' = []

    # Each round takes the next document of every kind that still has one left.
    while len(out) < document_count:
        for kind in kinds:
            if kind:
                document = kind.pop(0)
                out.append(document)

    return out

# ################################################################################################################################
# ################################################################################################################################
