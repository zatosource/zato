# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from random import Random
    Random = Random

# ################################################################################################################################
# ################################################################################################################################

# One order line of a business document, with an item, a price, a date and a site address,
# so that a document made of such lines compresses as much as business documents do.
_line_item = (
    '<LineItem><LineNumber>{line}</LineNumber><ProductCode>PRD-{product:06d}</ProductCode>'
    '<Description>{adjective} {noun} {variant}</Description><Quantity>{quantity}</Quantity>'
    '<UnitPrice currency="GBP">{price}.{pence:02d}</UnitPrice><RequiredDate>2026-{month:02d}-{day:02d}</RequiredDate>'
    '<SiteAddress><BuildingNumber>{building}</BuildingNumber><Street>{street} {street_kind}</Street>'
    '<Town>{town}</Town><Postcode>{area}{district} {sector}{unit}</Postcode></SiteAddress>'
    '<Reference>{reference:010d}</Reference><Status>{status}</Status></LineItem>\n'
)

_adjectives = ('Standard', 'Premium', 'Enhanced', 'Basic', 'Managed', 'Dedicated', 'Shared', 'Extended')
_nouns = ('Connection', 'Circuit', 'Termination', 'Port', 'Cabinet', 'Router', 'Line', 'Bandwidth Profile')
_variants = ('Type A', 'Type B', 'Type C', 'Single', 'Dual', 'Resilient', 'Temporary', 'Permanent')
_streets = ('Station', 'Church', 'Mill', 'Park', 'Victoria', 'Queen', 'Green', 'Manor', 'Kings', 'Bridge')
_street_kinds = ('Road', 'Street', 'Lane', 'Avenue', 'Close', 'Way', 'Gardens', 'Terrace')
_towns = ('Ashford', 'Barnsley', 'Carlisle', 'Dudley', 'Ely', 'Fareham', 'Grantham', 'Harlow', 'Ipswich', 'Kendal')
_statuses = ('Requested', 'Confirmed', 'Scheduled', 'Pending', 'Completed')
_postcode_letters = 'ABCDEFGHJKLMNPRSTUWXY'

# The ranges the numbers of a line are drawn from.
_max_product = 1_000_000
_max_quantity = 50
_max_price = 2_000
_pence_per_pound = 100
_months = 12
_max_day = 28
_max_building = 300
_max_district = 99
_max_sector = 9
_max_reference = 10_000_000_000

# ################################################################################################################################
# ################################################################################################################################

def _postcode_pair(draw:'Random') -> 'str':
    first = draw.choice(_postcode_letters)
    second = draw.choice(_postcode_letters)

    out = first + second
    return out

# ################################################################################################################################

def new_line_items(draw:'Random', size:'int') -> 'bytes':
    """ Returns whole order lines with values drawn at random, as many as reach the given size in bytes.
    """
    lines:'list[str]' = []
    total = 0
    line_number = 0

    while total < size:
        line_number += 1

        area = _postcode_pair(draw)
        unit = _postcode_pair(draw)

        line = _line_item.format(
            line=line_number,
            product=draw.randrange(_max_product),
            adjective=draw.choice(_adjectives),
            noun=draw.choice(_nouns),
            variant=draw.choice(_variants),
            quantity=draw.randint(1, _max_quantity),
            price=draw.randint(1, _max_price),
            pence=draw.randrange(_pence_per_pound),
            month=draw.randint(1, _months),
            day=draw.randint(1, _max_day),
            building=draw.randint(1, _max_building),
            street=draw.choice(_streets),
            street_kind=draw.choice(_street_kinds),
            town=draw.choice(_towns),
            area=area,
            district=draw.randint(1, _max_district),
            sector=draw.randint(0, _max_sector),
            unit=unit,
            reference=draw.randrange(_max_reference),
            status=draw.choice(_statuses),
        )

        lines.append(line)
        total += len(line)

    text = ''.join(lines)

    out = text.encode('utf8')
    return out

# ################################################################################################################################
# ################################################################################################################################
