# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A sample HL7 feed built as a wrapper over the shipped fakers - realistic ADT/ORU mixes
# at a configurable rate with injectable failures. This is a load driver and a demo asset:
# pointed at an MLLP channel it fills the dashboard and the message browser with live traffic,
# and the volume tests drive sustained load through it. No message content is authored here -
# every message comes from zato.hl7v2.tests.fakers.

# stdlib
from dataclasses import dataclass
from random import Random
from time import monotonic, sleep

# Zato
from zato.hl7v2.tests.fakers import fake
from zato.hl7v2.tests.fakers.msg_adt import fake_adta01, fake_adta02, fake_adta03, fake_adta05
from zato.hl7v2.tests.fakers.msg_oru import fake_orur01

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, callable_
    any_ = any_
    anylist = anylist
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

# How fast the feed runs unless configured otherwise
Default_Rate_Per_Minute = 600

# What fraction of messages carries the failure marker unless configured otherwise
Default_Error_Ratio = 0.0

# The MSH-3 sending application marking a message as an injected failure -
# a channel routes this value to an erroring service, which is how failures materialize
Default_Error_Sending_Application = 'ERROR_FEED_SYSTEM'

# The seed making a feed reproducible unless configured otherwise
Default_Seed = 12345

# The prefix of every control id the feed assigns
Control_Id_Prefix = 'FEED'

# How many seconds one minute holds - used when converting the rate to an interval
_seconds_per_minute = 60.0

# ################################################################################################################################
# ################################################################################################################################

# The default mix mirrors an ADT-heavy hospital feed with lab results alongside -
# each entry is a message type, its faker and its relative weight.
Default_Mix = (
    ('ADT^A01', fake_adta01, 30),
    ('ADT^A02', fake_adta02, 15),
    ('ADT^A03', fake_adta03, 15),
    ('ADT^A05', fake_adta05, 20),
    ('ORU^R01', fake_orur01, 20),
)

# ################################################################################################################################
# ################################################################################################################################

# Field indexes within a pipe-split MSH segment, where index 0 is the segment name itself
_MSH3_Index  = 2
_MSH10_Index = 9

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FeedConfig:
    """ How a feed run behaves - its rate, its error mix and its reproducibility.
    """

    # How many messages the feed sends per minute
    rate_per_minute:'int' = Default_Rate_Per_Minute

    # What fraction of messages carries the failure marker, 0.0 to 1.0
    error_ratio:'float' = Default_Error_Ratio

    # The MSH-3 value marking a message as an injected failure
    error_sending_application:'str' = Default_Error_Sending_Application

    # The seed the message mix and error placement are drawn from
    seed:'int' = Default_Seed

    # The message mix - (message type, faker, weight) triples
    mix:'tuple' = Default_Mix

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FeedItem:
    """ One message the feed produced, ready to send.
    """

    # The full ER7 message text
    text:'str' = ''

    # The message type, e.g. ADT^A01
    msg_type:'str' = ''

    # The control id the feed assigned - unique and sequential within a run
    control_id:'str' = ''

    # Whether this message carries the injected-failure marker
    is_error:'bool' = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FeedRunResult:
    """ What one feed run did - how many messages went out and how long each send took.
    """

    # How many messages were sent
    sent_count:'int' = 0

    # How many of them carried the injected-failure marker
    error_injected_count:'int' = 0

    # How long each send took, in milliseconds, in send order
    durations_ms:'anylist' = None # type: ignore[assignment]

# ################################################################################################################################
# ################################################################################################################################

def _rewrite_msh_field(message_text:'str', field_index:'int', value:'str') -> 'str':
    """ Returns the message with one MSH field replaced - how the feed assigns
    its own control ids and failure markers without authoring message content.
    """

    # The MSH segment is everything up to the first segment separator
    msh_line, separator, rest = message_text.partition('\r')

    fields = msh_line.split('|')
    fields[field_index] = value

    out = '|'.join(fields) + separator + rest
    return out

# ################################################################################################################################

def generate_feed_items(count:'int', config:'FeedConfig') -> 'anylist':
    """ Returns the messages of one feed run - the configured mix in random order,
    each with a unique sequential control id, the configured fraction of them
    carrying the failure marker. The same seed always produces the same feed.
    """

    # One generator drives both the mix and the error placement, and the shared faker
    # underneath the message content is reseeded too, so a seed fixes the whole run.
    # The instance is seeded directly because a class-level seed stops applying
    # once anything anywhere seeded the instance, e.g. another test module.
    random_source = Random(config.seed)
    fake.seed_instance(config.seed)

    # The weighted-choice inputs are unzipped out of the mix once
    entries = [(msg_type, faker) for msg_type, faker, _ in config.mix]
    weights = [weight for _, _, weight in config.mix]

    # Our response to produce
    out:'anylist' = []

    for index in range(count):

        msg_type, faker = random_source.choices(entries, weights=weights)[0]

        item = FeedItem()
        item.msg_type = msg_type
        item.control_id = f'{Control_Id_Prefix}-{index + 1:08d}'
        item.is_error = random_source.random() < config.error_ratio

        # The faker authors the message, the feed only stamps its own control id ..
        text = faker()
        text = _rewrite_msh_field(text, _MSH10_Index, item.control_id)

        # .. and an injected failure is a routing marker, not corrupted content -
        # a channel routes this MSH-3 value to a service that fails.
        if item.is_error:
            text = _rewrite_msh_field(text, _MSH3_Index, config.error_sending_application)

        item.text = text
        out.append(item)

    return out

# ################################################################################################################################

def run_feed(
    send:'callable_',
    count:'int',
    config:'FeedConfig',
    *,
    sleep_func:'callable_' = sleep,
    ) -> 'FeedRunResult':
    """ Sends one feed run through the given callable, pacing the sends to the configured
    rate, and returns what happened. The send callable receives one FeedItem at a time.
    The sleep function is injectable so tests can run the pacing logic offline.
    """

    items = generate_feed_items(count, config)

    # The gap between two sends that yields the configured rate
    interval = _seconds_per_minute / config.rate_per_minute

    # Our response to produce - the list is assigned here because a dataclass
    # built with init=False never runs its field factories.
    out = FeedRunResult()
    out.durations_ms = []

    # The pacing is drift-free - each send is scheduled off the run's start,
    # not off the previous send, so a slow send does not slow the whole feed down.
    run_start = monotonic()

    for index, item in enumerate(items):

        # Wait until this message's scheduled time
        scheduled_at = run_start + (index * interval)
        wait = scheduled_at - monotonic()

        if wait > 0:
            sleep_func(wait)

        send_start = monotonic()
        _ = send(item)
        duration_ms = (monotonic() - send_start) * 1000

        out.sent_count += 1
        out.durations_ms.append(duration_ms)

        if item.is_error:
            out.error_injected_count += 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ The demo entry point - sends a feed over MLLP to the given address, so a fresh
    install shows a live dashboard and a searchable browser from the first minute.
    """

    # stdlib
    import argparse

    # Zato
    from zato.common.api import HL7
    from zato.common.hl7.mllp.client import HL7MLLPClient
    from zato.common.util.api import hex_sequence_to_bytes
    from zato.common.util.tcp import parse_address

    parser = argparse.ArgumentParser(description='Sends a sample HL7 feed to an MLLP address')
    _ = parser.add_argument('--address', required=True, help='The host:port to send to')
    _ = parser.add_argument('--count', type=int, default=100, help='How many messages to send')
    _ = parser.add_argument('--rate', type=int, default=Default_Rate_Per_Minute, help='Messages per minute')
    _ = parser.add_argument('--error-ratio', type=float, default=Default_Error_Ratio, help='Fraction of injected failures')
    _ = parser.add_argument('--seed', type=int, default=Default_Seed, help='The seed making the run reproducible')

    args = parser.parse_args()

    host, port_string = parse_address(args.address)
    port = int(port_string)

    client = HL7MLLPClient(
        host,
        port,
        hex_sequence_to_bytes(HL7.Default.start_seq),
        hex_sequence_to_bytes(HL7.Default.end_seq),
    )

    config = FeedConfig()
    config.rate_per_minute = args.rate
    config.error_ratio = args.error_ratio
    config.seed = args.seed

    def send(item:'FeedItem') -> 'None':
        _ = client.send(item.text.encode('utf-8'), item.control_id)

    result = run_feed(send, args.count, config)

    print(f'Sent {result.sent_count} messages ({result.error_injected_count} with injected failures)')

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
