# Zato Pub/Sub Topic Pattern Matching

## Overview

Zato's pub/sub system uses pattern matching to control access to topics. Patterns allow you to define flexible rules
for which topics a client can publish to or subscribe from, without having to specify each topic individually.

## Topic Name Restrictions

Topic names must adhere to the following rules:
- Maximum length: 200 characters
- The "#" character is not allowed in topic names
- Only ASCII characters are permitted

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
6. **Alphabetical Evaluation**: Patterns are evaluated in alphabetical order, and wildcards are evaluated last

   Example: Given patterns `orders.*`, `orders.urgent`, `alerts.**`, `alerts.critical`, the evaluation order is:
   1. `alerts.critical` (alphabetical, no wildcards)
   2. `alerts.**` (alphabetical, has wildcards)
   3. `orders.urgent` (alphabetical, no wildcards)
   4. `orders.*` (alphabetical, has wildcards)

7. **First Match Wins**: Evaluation stops at the first matching pattern

## FAQ

### Q: Can I use wildcards at the beginning of a pattern?
**A:** Yes. `*.orders` matches `urgent.orders`, `daily.orders`, etc.

### Q: What's the difference between `*` and `**`?
**A:** `*` stops at dots, `**` crosses them, so `topic.*` matches `topic.abc` but not `topic.abc.def`, while `topic.**` matches both.

### Q: Can I mix wildcards in one pattern?
**A:** Yes. `orders.*.processed.**` matches `orders.urgent.processed.daily` and `orders.bulk.processed.summary.final`.

### Q: Does ** match to the end of a topic name?
**A:** Yes. When ** appears at the end of a pattern like `orders.**`, it matches `orders.urgent`, `orders.urgent.high`,
and `orders.urgent.high.priority`. The ** wildcard matches zero or more segments from its position to the end of the topic name.

### Q: Can I use ** in the middle of a pattern?
**A:** Yes. `orders.**.new` matches `orders.new`, `orders.urgent.new`, `orders.urgent.high.new`, and `orders.a.b.c.d.new`.
The ** wildcard matches zero or more segments between its position and the next literal part of the pattern.

### Q: Can I have empty segments?
**A:** Yes. E.g. `orders..123` (double dot) will be treated as this exact, literal name, "orders", then two dots and then "123".

### Q: Can I use other wildcard characters like `?` or `>`?
**A:** No. Only `*` and `**` are supported wildcards.

### Q: What happens if I have overlapping patterns?
**A:** Only the first matching pattern applies due to the "first match wins" rule. If you have both `orders.*`
and `orders.urgent`, `orders.urgent` comes first (exact patterns before wildcards), so `orders.urgent` will be evaluated first for topic `orders.urgent`.

### Q: Are there any reserved topic names?
**A:** Yes. Topic names cannot contain "zato" or "zpsk" anywhere in the name (case insensitive). Additionally, all topic names must contain only ASCII characters - Unicode characters are not allowed. Also avoid using dots at the start or end of topic names for clarity.

### Q: How do I match topics with special characters?
**A:** Special characters (except dots and wildcards) are treated literally. `orders-2024` matches exactly `orders-2024`.

### Q: In what order are patterns evaluated?
**A:** Patterns are evaluated alphabetically and the first match wins, and wildcards are evaluated last. This means:

```
Given patterns:
- sub=transaction.priority
- sub=transaction.*
- sub=transaction.**.processed
- sub=transaction.international

Evaluation order:
1. transaction.international
2. transaction.priority
3. transaction.*
4. transaction.**.processed
```

**Example 1:** When a message is sent to topic `transaction.international`, the system will check:
* First, `transaction.international` (matches)
* Evaluation stops here - remaining patterns are skipped

**Example 2:** When a message is sent to topic `transaction.domestic`, the system will check:
* First, `transaction.international` (no match)
* Then `transaction.priority` (no match)
* Then `transaction.*` (matches)
* Evaluation stops here - `transaction.**.processed` is skipped

**Example 3:** When a message is sent to topic `transaction.wire.processed`, the system will check:
* First, `transaction.international` (no match)
* Then `transaction.priority` (no match)
* Then `transaction.*` (no match)
* Finally `transaction.**.processed` (matches)
