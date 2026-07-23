# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# humanize
from humanize import intcomma

# Local
from common import Floors, Measurement, PerfDatabase, Seeded_Definition_Count
from zato.common.rule_engine.sql import RuleSQLBackend
from seeding import delete_all_rows, Seed_Definition_Base, Seed_Versions_Per_Definition, seed_definitions
from traffic import Author, create_rulesets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from common import measurement_list

    measurement_list = measurement_list

# ################################################################################################################################
# ################################################################################################################################

# The one searchable term the content search looks for across every seeded document.
Search_Term = 'network-tier-0042'

# The listing page must hold every child of one parent, so the crowd is what is measured.
List_Limit = 5_000

# ################################################################################################################################
# ################################################################################################################################

def run_definitions_scenario(backend:'RuleSQLBackend', database:'PerfDatabase', floors:'Floors') -> 'measurement_list':
    """ The editor paths over thousands of definitions - listing, content search, live resolution
    and one optimistic edit-and-publish cycle in the middle of the crowd, each under its ceiling.
    """
    print(f'Definitions: {intcomma(Seeded_Definition_Count)} definitions with versions and events', flush=True)

    # Start from empty tables, create the two parents, then bulk-seed the crowd around them ..
    delete_all_rows(database)
    ruleset_ids = create_rulesets(backend)
    seed_seconds = seed_definitions(database, ruleset_ids)
    print(f'Definitions: seeded in {seed_seconds:.2f}s', flush=True)

    ceiling = floors.max_definition_query_seconds
    admin_id = ruleset_ids[0]

    # .. list every child of one parent - the crowded editor tree ..
    start = monotonic()
    children = backend.definitions.list(parent_id=admin_id, limit=List_Limit)
    now = monotonic()
    list_seconds = now - start

    child_count = len(children)
    expected_children = (Seeded_Definition_Count - 2) // 2
    assert child_count == expected_children, f'Expected {expected_children} children, found {child_count}'
    assert list_seconds <= ceiling, f'Definition list too slow: {list_seconds:.3f}s, ceiling {ceiling}s'

    # .. search by content across every seeded document - the editor's search-as-you-type path ..
    start = monotonic()
    matches = backend.definitions.list(parent_id=admin_id, search_text=Search_Term, limit=List_Limit)
    now = monotonic()
    search_seconds = now - start

    match_count = len(matches)
    assert match_count > 0, 'The content search found nothing'
    assert search_seconds <= ceiling, f'Content search too slow: {search_seconds:.3f}s, ceiling {ceiling}s'

    # .. resolve one live version in the middle of the crowd - what invocation does before evaluating ..
    child_id = Seed_Definition_Base + expected_children
    start = monotonic()
    live = backend.versions.get_live(child_id)
    now = monotonic()
    live_seconds = now - start

    assert live.version == Seed_Versions_Per_Definition
    assert live_seconds <= ceiling, f'Live resolution too slow: {live_seconds:.3f}s, ceiling {ceiling}s'

    # .. and run one optimistic edit-and-publish cycle - the editor's save path.
    document = {'conditions': [{'term': 'member.plan', 'operator': 'equals', 'value': 'plan-complete'}]}
    start = monotonic()
    version = backend.versions.create(
        definition_id=child_id,
        expected_current_version=Seed_Versions_Per_Definition,
        document=document,
        author=Author,
        comment='Refine the plan condition after review',
    )
    _ = backend.versions.publish(definition_id=child_id, version=version.version, actor=Author)
    now = monotonic()
    publish_seconds = now - start

    assert publish_seconds <= ceiling, f'Edit and publish too slow: {publish_seconds:.3f}s, ceiling {ceiling}s'

    timings = f'list {list_seconds:.3f}s, search {search_seconds:.3f}s, live {live_seconds:.3f}s, publish {publish_seconds:.3f}s'
    print(f'Definitions: {timings}', flush=True)

    out = [
        Measurement('Definition list seconds', f'{list_seconds:.3f}', f'<= {ceiling}s'),
        Measurement('Definition content search seconds', f'{search_seconds:.3f}', f'<= {ceiling}s'),
        Measurement('Definition live resolution seconds', f'{live_seconds:.3f}', f'<= {ceiling}s'),
        Measurement('Definition edit and publish seconds', f'{publish_seconds:.3f}', f'<= {ceiling}s'),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################
