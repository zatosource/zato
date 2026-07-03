from __future__ import annotations

# Plain type aliases rather than NewType - user code assigns literals directly
# (patient.active = True, observation.status = 'final') and NewType would reject
# every such assignment under a type checker.

Boolean = bool
Integer = int
String = str
Decimal = str
Uri = str
Url = str
Canonical = str
Base64Binary = str
Instant = str
Date = str
DateTime = str
Time = str
Code = str
Oid = str
Id = str
Markdown = str
UnsignedInt = int
PositiveInt = int
Uuid = str
Xhtml = str
