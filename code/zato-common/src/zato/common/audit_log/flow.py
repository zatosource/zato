# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

One event's flow - every event related to it, found by widening a seed four ways and then read
forward in time. All four ways are already in the data, so this answers for every source rather
than for any one of them:

- the same cid is the operation itself, a request and its response, a message and its ack, and the
  fan-out of a channel to its destinations, which is the one place a single cid crosses sources
- an event_link, read in both directions, is batch membership and resubmission
- a correl_id bridge is a resubmission naming the event it was born from by that event's cid
- the same (source, msg_id) is how AS2 MDNs, AS4 receipts and X12 acks pair with what they answer,
  since those never share a cid with it
"""

# stdlib
from dataclasses import dataclass, field

# SQLAlchemy
from sqlalchemy import and_, or_, select

# Zato
from zato.common.audit_log.api import event_link_table, event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intdict, intlist, intstrdict, strintdict
    any_ = any_
    anylist = anylist
    intdict = intdict
    intlist = intlist
    intstrdict = intstrdict
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

# Why one event is in another's flow, which is what a line of the flow says about itself
Relation_Seed = 'seed'
Relation_Same_Cid = 'same-cid'
Relation_Parent = 'parent'
Relation_Child = 'child'
Relation_Resubmit_Of = 'resubmit-of'
Relation_Resubmitted_As = 'resubmitted-as'
Relation_Same_Msg_Id = 'same-msg-id'

# What a search term resolved as, which is what the journey endpoint reports back
Resolved_Event_Id = 'event-id'
Resolved_Cid = 'cid'
Resolved_Msg_Id = 'msg-id'

# A flow past this many events is one nobody reads to the end, and the query behind it stops
# being cheap, so it is cut short and the reader is told that it was
Max_Flow_Events = 200

# A resubmit of a batch item of a resubmit is as deep as anything seen in the field
Max_Flow_Rounds = 4

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ResolvedSeed:
    """ What one search term led to - the event a flow is read from and which of the term's
    possible meanings it turned out to carry, both empty when the term matched nothing.
    """
    seed_id: int = 0
    resolved_by: str = ''

# ################################################################################################################################

def _new_resolved_seed() -> 'ResolvedSeed':
    out = ResolvedSeed()
    out.seed_id = 0
    out.resolved_by = ''

    return out

# ################################################################################################################################

def _newest_event_id(connection:'any_', column:'any_', term:'str') -> 'int':
    """ The newest event whose given column carries the term, zero when there is none -
    two events of one moment are told apart by their ids, the way the flow itself reads.
    """
    statement = select(event_table.c.id)
    statement = statement.where(column == term)
    statement = statement.order_by(event_table.c.event_time_iso.desc(), event_table.c.id.desc())
    statement = statement.limit(1)

    row = connection.execute(statement).fetchone()

    if row is None:
        return 0

    return row[0]

# ################################################################################################################################

def resolve_seed(connection:'any_', term:'str') -> 'ResolvedSeed':
    """ Resolves one search term to the event a flow is read from. The term is tried as an
    event id, then as a cid, then as a control id (msg_id) - the first meaning that matches
    wins, and within one meaning the newest matching event does. A term that matches nothing
    resolves to nothing, which the caller reads off the empty resolved_by.
    """
    out = _new_resolved_seed()

    # A term of digits alone may be the event's own number, which is the most exact
    # of the three meanings, so it is tried first
    if term.isdigit():
        statement = select(event_table.c.id)
        statement = statement.where(event_table.c.id == int(term))

        row = connection.execute(statement).fetchone()

        if row is not None:
            out.seed_id = row[0]
            out.resolved_by = Resolved_Event_Id
            return out

    # .. then the cid the message travelled under ..
    event_id = _newest_event_id(connection, event_table.c.cid, term)

    if event_id:
        out.seed_id = event_id
        out.resolved_by = Resolved_Cid
        return out

    # .. and last the control id the message's own protocol knows it by.
    event_id = _newest_event_id(connection, event_table.c.msg_id, term)

    if event_id:
        out.seed_id = event_id
        out.resolved_by = Resolved_Msg_Id

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FlowIds:
    """ The events of one flow - which they are, why each of them is in it, which held event each
    of them was found through, plus whether the widening was stopped before it ran out of events
    to find. An event found by sharing a cid or a message id has no via - those relations name no
    one event in particular.
    """
    relation_by_id: 'intstrdict' = field(default_factory=dict)
    via_by_id: 'intdict' = field(default_factory=dict)
    is_truncated: bool = False

# ################################################################################################################################

def _new_flow_ids() -> 'FlowIds':
    out = FlowIds()
    out.relation_by_id = {}
    out.via_by_id = {}
    out.is_truncated = False

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _Frontier:
    """ What the events of one round are known by, which is what the next round widens on, and the
    id of the held event behind each cid and each named origin, so whatever a cid leads to can be
    traced back to the event it was found through.
    """
    cids: 'anylist' = field(default_factory=list)
    correl_ids: 'anylist' = field(default_factory=list)
    msg_id_pairs: 'anylist' = field(default_factory=list)
    ids: 'intlist' = field(default_factory=list)
    id_by_cid: 'strintdict' = field(default_factory=dict)
    id_by_correl_id: 'strintdict' = field(default_factory=dict)

# ################################################################################################################################

def _read_frontier(connection:'any_', ids:'intlist') -> '_Frontier':
    """ Reads what the events of one round are known by - the cids they travelled under, the cids
    they name as their origin, and the (source, message id) pairs an acknowledgment would echo.
    """
    out = _Frontier()
    out.cids = []
    out.correl_ids = []
    out.msg_id_pairs = []
    out.ids = ids
    out.id_by_cid = {}
    out.id_by_correl_id = {}

    statement = select(
        event_table.c.id,
        event_table.c.cid,
        event_table.c.correl_id,
        event_table.c.msg_id,
        event_table.c.source,
    )
    statement = statement.where(event_table.c.id.in_(ids))

    result = connection.execute(statement)

    for event_id, cid, correl_id, msg_id, source in result:

        if cid:
            out.cids.append(cid)
            out.id_by_cid[cid] = event_id

        # An event naming an origin is a resubmission, and the cid it names is the original's own
        if correl_id:
            out.correl_ids.append(correl_id)
            out.id_by_correl_id[correl_id] = event_id

        # A message id is only a pair with the source that issued it - two sources may well
        # number their messages the same way
        if msg_id:
            out.msg_id_pairs.append((source, msg_id))

    return out

# ################################################################################################################################

def _select_same_cid(frontier:'_Frontier') -> 'any_':
    """ The operation itself - every event that travelled under one of the cids already held.
    """
    statement = select(event_table.c.id)
    statement = statement.where(event_table.c.cid.in_(frontier.cids))

    return statement

# ################################################################################################################################

def _select_resubmits_of_held(frontier:'_Frontier') -> 'any_':
    """ The resubmissions born from the events already held - each of them names one of their cids
    as the cid of the message it is sending out again. The named cid rides along so each found
    resubmission can be traced back to the held event it was born from.
    """
    statement = select(event_table.c.id, event_table.c.correl_id)
    statement = statement.where(event_table.c.correl_id.in_(frontier.cids))

    return statement

# ################################################################################################################################

def _select_origins_of_held(frontier:'_Frontier') -> 'any_':
    """ The other end of the same arrow - the original messages that the events already held were
    born from, found by the cid each of those events names as its origin. The cid rides along so
    each found original can be traced back to the resubmission that named it.
    """
    statement = select(event_table.c.id, event_table.c.cid)
    statement = statement.where(event_table.c.cid.in_(frontier.correl_ids))

    return statement

# ################################################################################################################################

def _select_same_msg_id(frontier:'_Frontier') -> 'any_':
    """ The acknowledgments that pair with what they answer by echoing its message id, and what they
    answer - a pairing that carries no cid in common at all.
    """
    pair_conditions:'anylist' = []

    for source, msg_id in frontier.msg_id_pairs:
        is_same_pair = and_(
            event_table.c.source == source,
            event_table.c.msg_id == msg_id,
        )
        pair_conditions.append(is_same_pair)

    statement = select(event_table.c.id)
    statement = statement.where(or_(*pair_conditions))

    return statement

# ################################################################################################################################

def _add_found(flow_ids:'FlowIds', found:'anylist', relation:'str', new_ids:'intlist') -> 'None':
    """ Records the events one widening step found, each a pair of the event's own id and the id of
    the held event it was found through, zero when the relation names no one event in particular.
    The first relation an event is found under is the one it keeps - a batch item that also shares
    the seed's cid is read as the batch item it is, because the steps run from the closest relation
    outwards - and the via it keeps is the one recorded alongside that first relation.
    """
    for event_id, via_id in found:

        if event_id in flow_ids.relation_by_id:
            continue

        # A flow already at its ceiling takes nothing more, and says so
        if len(flow_ids.relation_by_id) >= Max_Flow_Events:
            flow_ids.is_truncated = True
            return

        flow_ids.relation_by_id[event_id] = relation
        new_ids.append(event_id)

        if via_id:
            flow_ids.via_by_id[event_id] = via_id

# ################################################################################################################################

def _run_step(connection:'any_', statement:'any_', flow_ids:'FlowIds', relation:'str', new_ids:'intlist') -> 'None':
    """ One widening step whose relation is shared rather than pointed - runs its select and records
    whatever of it is not in the flow yet, with no via for any of it.
    """
    result = connection.execute(statement)
    found:'anylist' = []

    for db_row in result:
        found.append((db_row[0], 0))

    _add_found(flow_ids, found, relation, new_ids)

# ################################################################################################################################

def _run_via_step(connection:'any_', statement:'any_', via_by_key:'strintdict', flow_ids:'FlowIds', relation:'str', new_ids:'intlist') -> 'None':
    """ One widening step whose relation points at one held event - the select returns each found
    event together with the cid that led to it, and the map turns that cid back into the id of the
    held event it belongs to.
    """
    result = connection.execute(statement)
    found:'anylist' = []

    for event_id, key in result:
        found.append((event_id, via_by_key[key]))

    _add_found(flow_ids, found, relation, new_ids)

# ################################################################################################################################

def _widen_by_links(connection:'any_', frontier:'_Frontier', flow_ids:'FlowIds', new_ids:'intlist') -> 'None':
    """ The lineage of the events already held, read both ways - what they came out of and what came
    out of them, which is batch membership on one side and resubmission on the other. Either way the
    held end of the link is the via of the event the link finds.
    """
    parents_statement = select(event_link_table.c.parent_event_id, event_link_table.c.child_event_id)
    parents_statement = parents_statement.where(event_link_table.c.child_event_id.in_(frontier.ids))

    result = connection.execute(parents_statement)
    found:'anylist' = []

    for parent_event_id, child_event_id in result:
        found.append((parent_event_id, child_event_id))

    _add_found(flow_ids, found, Relation_Parent, new_ids)

    children_statement = select(event_link_table.c.child_event_id, event_link_table.c.parent_event_id)
    children_statement = children_statement.where(event_link_table.c.parent_event_id.in_(frontier.ids))

    result = connection.execute(children_statement)
    found = []

    for child_event_id, parent_event_id in result:
        found.append((child_event_id, parent_event_id))

    _add_found(flow_ids, found, Relation_Child, new_ids)

# ################################################################################################################################

def get_flow_ids(connection:'any_', seed_id:'int') -> 'FlowIds':
    """ Returns the events of one event's flow - the id of each of them, why it is in the flow, and
    whether the widening was cut short by the ceiling on how large a flow is read at once.
    """
    out = _new_flow_ids()
    out.relation_by_id[seed_id] = Relation_Seed

    # Each round widens on what the round before it found, and a round that finds nothing new
    # is where the flow ends
    frontier_ids:'intlist' = [seed_id]

    for _ in range(Max_Flow_Rounds):

        # An event with nothing left to widen on ends the flow here
        if not frontier_ids:
            break

        frontier = _read_frontier(connection, frontier_ids)
        new_ids:'intlist' = []

        # The operation the events belong to comes first, because it is the closest relation
        # any of them has ..
        if frontier.cids:
            _run_step(connection, _select_same_cid(frontier), out, Relation_Same_Cid, new_ids)

        # .. then their lineage in both directions ..
        _widen_by_links(connection, frontier, out, new_ids)

        # .. then the resubmission arrow, which is a cid named rather than shared, read from
        # each of its two ends, either end tracing back to the held event at the other ..
        if frontier.cids:
            _run_via_step(connection, _select_resubmits_of_held(frontier), frontier.id_by_cid, out, Relation_Resubmit_Of, new_ids)

        if frontier.correl_ids:
            _run_via_step(connection, _select_origins_of_held(frontier), frontier.id_by_correl_id, out, Relation_Resubmitted_As, new_ids)

        # .. and last the pairing by message id, which is the only one of the four that says
        # nothing about who wrote either event down.
        if frontier.msg_id_pairs:
            _run_step(connection, _select_same_msg_id(frontier), out, Relation_Same_Msg_Id, new_ids)

        # A flow stopped at its ceiling is not widened any further
        if out.is_truncated:
            break

        frontier_ids = new_ids

    return out

# ################################################################################################################################
# ################################################################################################################################
