# Zato Pub/Sub Topic Pattern Matching

## Overview

Zato's pub/sub system uses pattern matching to control access to topics. Patterns allow you to define flexible rules
for which topics a client can publish to or subscribe from, without having to specify each topic individually.

## Pattern Types

### Exact Match
When no wildcards are used, the pattern must match the topic name exactly.

```
Pattern: orders.processed
Matches: orders.processed
Does not match: orders.processed.daily, orders.pending
```

### Single Wildcard (`*`)
Matches any characters within a single topic segment (stops at dots).

```
Pattern: orders.*
Matches: orders.processed, orders.pending, orders.cancelled
Does not match: orders.processed.daily, orders.pending.urgent
```

### Multi-Level Wildcard (`**`)
Matches any characters across multiple topic segments (crosses dots).

```
Pattern: orders.**
Matches: orders.processed, orders.processed.daily, orders.pending.urgent.high
Does not match: inventory.low, users.created
```

## Usage Examples

### Publisher Patterns
```
pub=notifications.**
- Can publish to: notifications.email, notifications.sms.urgent, notifications.push.mobile.ios

pub=events.user.*
- Can publish to: events.user.created, events.user.updated, events.user.deleted
- Cannot publish to: events.user.profile.changed, events.system.started
```

### Subscriber Patterns
```
sub=alerts.critical.**
- Can subscribe to: alerts.critical.system, alerts.critical.database.connection, alerts.critical.security.breach

sub=logs.*.error
- Can subscribe to: logs.app.error, logs.db.error, logs.auth.error
- Cannot subscribe to: logs.app.debug.error, logs.system.warning
```

### Combined Access
A security definition can have multiple patterns for different access types:

```
pub=commands.user.**
sub=events.user.*
sub=notifications.user.email
```

This allows publishing to any user command topic, subscribing to direct user events, and subscribing to user email notifications.

## Pattern Matching Rules

1. **Segment Separation**: Topic names are separated by dots (`.`)
2. **Single Wildcard (`*`)**: Matches exactly one segment
3. **Multi-Level Wildcard (`**`)**: Matches one or more segments
4. **Case Insensitive**: All matching is case-insensitive
5. **No Partial Matches**: Patterns must match the complete topic name
6. **Alphabetical Evaluation**: Patterns are evaluated in alphabetical order
7. **First Match Wins**: Evaluation stops at the first matching pattern

## FAQ

### Q: Can I use wildcards at the beginning of a pattern?
**A:** Yes. `*.orders` matches `urgent.orders`, `daily.orders`, etc.

### Q: What's the difference between `*` and `**`?
**A:** `*` stops at dots, `**` crosses them, so `topic.*` matches `topic.abc` but not `topic.abc.def`, but `topic.**` matches both.

### Q: Can I mix wildcards in one pattern?
**A:** Yes. `orders.*.processed.**` matches `orders.urgent.processed.daily` and `orders.bulk.processed.summary.final`.

### Q: Do patterns work with empty segments?
**A:** No. `topic..name` (double dot) is not valid and won't match patterns like `topic.*.name`.

### Q: Can I use other wildcard characters like `?`?
**A:** No. Only `*` and `**` are supported wildcards.

### Q: What happens if I have overlapping patterns?
**A:** All matching patterns apply. If you have both `orders.*` and `orders.urgent`, both will match `orders.urgent`.

### Q: Are there any reserved topic names?
**A:** No specific reserved names, but avoid using dots at the start or end of topic names for clarity.

### Q: How do I match topics with special characters?
**A:** Special characters (except dots and wildcards) are treated literally. `orders-2024` matches exactly `orders-2024`.

### Q: In what order are patterns evaluated?
**A:** Patterns are evaluated alphabetically and the first match wins. This means:

```
Given patterns:
- sub=orders.urgent
- sub=orders.*
- sub=orders.**.processed

Evaluation order:
1. orders.* (comes first alphabetically)
2. orders.**.processed
3. orders.urgent
```

For instance, when a message is sent to topic `ZZZ.urgent`, the system will check the publisher's publication permissions in this order:

* First, `ZZZ.*` first (no match)
* Then `ZZZ.**.processed` (matches)
* and the last one `ZZZ` will be skipped because the previous one already matched, although otherwise it would've been a match
