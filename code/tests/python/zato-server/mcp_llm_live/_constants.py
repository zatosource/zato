# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

# JSON-RPC 2.0 error codes used across the suite
Error_Invalid_Request  = -32600
Error_Method_Not_Found = -32601
Error_Invalid_Params   = -32602

# JSON-RPC error code returned when a request asks for a protocol version the server does not speak
Error_Unsupported_Protocol_Version = -32022

# The protocol revisions the server speaks
Protocol_Version_Sessions  = '2025-06-18'
Protocol_Version_Stateless = '2026-07-28'

# The name the shared stateless client imports the revision under
_protocol_version_stateless = Protocol_Version_Stateless

# ################################################################################################################################
# ################################################################################################################################

# The CRM services the suite deploys - the whole point is that they are custom, not the built-in demos
Service_Customer_Get = 'crm.customer.get'
Service_Invoice_List = 'crm.invoice.list'
Service_Order_Status = 'crm.order.status'
Service_Order_Cancel = 'crm.order.cancel'
Service_Deploy_Probe = 'crm.deploy.probe'

# Further CRM services - reference facts, accounts, slow echoes, confirmations, padded text and reports
Service_Fact_Get        = 'crm.fact.get'
Service_Account_Lookup  = 'crm.account.lookup'
Service_Account_Query   = 'crm.account.query'
Service_Echo_Slow       = 'crm.echo.slow'
Service_Order_Confirm   = 'crm.order.confirm'
Service_Text_Pad        = 'crm.text.pad'
Service_Customer_List   = 'crm.customer.list'
Service_Report_Build    = 'crm.report.build'
Service_Docstring_Probe = 'crm.docstring.probe'
Service_Blank_Probe     = 'crm.blank.probe'

# Every CRM service except the hot-deploy probe, which has a gateway of its own
Service_List_CRM = [Service_Customer_Get, Service_Invoice_List, Service_Order_Status, Service_Order_Cancel]

# The customer id every test asks about and the order ids the order services answer for
Customer_ID              = 'CRM-1001'
Order_ID                 = 'ORD-7002'
Order_ID_Not_Cancellable = 'ORD-7003'

# What crm.customer.get returns for the known customer - the values the LLM's final answer must carry
Customer_Name  = 'Renata Brixen'
Customer_City  = 'Innsbruck'
Customer_Email = 'renata.brixen@example.com'

# The three IMEIs of the customer's devices, each in a different written form, all with valid checksums
Customer_IMEI_Compact = '490154203237518'
Customer_IMEI_Dashed  = '35-209900-176148-1'
Customer_IMEI_Spaced  = '86 723902 235411 8'

# An IMEI whose checksum is broken - PII validation must leave it alone
Customer_IMEI_Invalid = '490154203237519'

# The IPv4 address that appears twice in the record, for the stable-replacement assertions
Customer_IPv4 = '203.0.113.77'

# The URLs the customer record carries - one on the safety gateways' allowed hosts list, one not
Customer_URL_Allowed    = 'https://example.com/crm/docs'
Customer_URL_Disallowed = 'https://tracking.invalid/pixel'

# What the order status service reports
Order_Status  = 'shipped'
Order_Carrier = 'DHL'

# The Greek and Japanese customers - non-ASCII names with PII of their own
Customer_ID_Greek    = 'CRM-2001'
Customer_ID_Japanese = 'CRM-3001'

Customer_Name_Greek    = 'Νίκος Παπαδόπουλος'
Customer_City_Greek    = 'Αθήνα'
Customer_Name_Japanese = '山田太郎'
Customer_City_Japanese = '東京'

# The Greek record's two distinct emails, in one contacts line, for the distinct-replacement assertions
Customer_Email_Greek   = 'nikos.papadopoulos@example.com'
Customer_Email_Greek_B = 'n.papadopoulos@example.org'

# The Japanese record's email and IMEI, nested in objects and arrays, and its national id
# that only the jp land's detectors recognize
Customer_Email_Japanese       = 'taro.yamada@example.com'
Customer_IMEI_Japanese        = '490154203237518'
Customer_National_ID_Japanese = '123456789018'

# What the reference service answers for the capital question and what the real answer is -
# the model must repeat the tool's value, not the well-known one
Fact_Answer       = 'Perth'
Fact_Answer_Known = 'Canberra'

# How long the slow echo service sleeps, in seconds
Slow_Echo_Seconds = 2

# ################################################################################################################################
# ################################################################################################################################

# The skill the skills gateway serves and the marker phrase its instructions mandate
Skill_House_Style = 'crm-house-style'
Skill_Marker      = 'CRM-HOUSE-STYLE-REPORT'

# A skill that exists on disk but is assigned to no gateway
Skill_Unassigned = 'crm-unassigned'

# The skill only the B side of the isolation pair serves
Skill_Iso_B = 'crm-iso-b'

# ################################################################################################################################
# ################################################################################################################################

# Security definitions the enmasse import creates
Sec_Basic          = 'test.llm.basic'
Sec_Basic_B        = 'test.llm.basic.b'
Sec_Basic_Shared   = 'test.llm.basic.shared'
Sec_APIKey         = 'test.llm.apikey'
Sec_Bearer_Static  = 'test.llm.bearer.static'
Sec_Bearer_Keycloak = 'test.llm.bearer.keycloak'

# Credentials of the definitions above - the passwords are random per run
Username_Basic        = 'test.llm.user'
Username_Basic_B      = 'test.llm.user.b'
Username_Basic_Shared = 'test.llm.user.shared'

Password_Basic        = 'test.llm.' + rand_string()
Password_Basic_B      = 'test.llm.b.' + rand_string()
Password_Basic_Shared = 'test.llm.shared.' + rand_string()

# The API key value and the header it travels in
APIKey_Value  = 'test.llm.key.' + rand_string()
APIKey_Header = 'X-API-Key'

# The static bearer token value
Bearer_Static_Token = 'test.llm.bearer.' + rand_string()

# Security groups
Group_Main   = 'llm.test-group-main'
Group_Iso_A  = 'llm.test-group-iso-a'
Group_Iso_B  = 'llm.test-group-iso-b'
Group_Iso_C  = 'llm.test-group-iso-c'
Group_Shared_A = 'llm.test-group-shared-a'
Group_Shared_B = 'llm.test-group-shared-b'

# ################################################################################################################################
# ################################################################################################################################

# The gateways the suite creates, one per capability family - names and URL paths
Gateway_Main             = 'test.llm.main'
Gateway_Validate         = 'test.llm.validate'
Gateway_Skills           = 'test.llm.skills'
Gateway_Shaping_Truncate = 'test.llm.shaping.truncate'
Gateway_Shaping_Block    = 'test.llm.shaping.block'
Gateway_Shaping_Threshold = 'test.llm.shaping.threshold'
Gateway_Shaping_Wide     = 'test.llm.shaping.wide'
Gateway_Shaping_Narrow   = 'test.llm.shaping.narrow'
Gateway_Compaction       = 'test.llm.compaction'
Gateway_PII              = 'test.llm.pii'
Gateway_PII_Exclude      = 'test.llm.pii.exclude'
Gateway_PII_Other_Land   = 'test.llm.pii.other-land'
Gateway_Safety           = 'test.llm.safety'
Gateway_Safety_Reject    = 'test.llm.safety.reject'
Gateway_Filters          = 'test.llm.filters'
Gateway_Lifecycle        = 'test.llm.lifecycle'
Gateway_Hotdeploy        = 'test.llm.hotdeploy'
Gateway_Iso_A            = 'test.llm.iso.a'
Gateway_Iso_B            = 'test.llm.iso.b'
Gateway_Iso_C            = 'test.llm.iso.c'

# Further gateways - the model's conduct, sessions, runtime changes,
# the pipeline's interplay, and one gateway per remaining option variant
Gateway_Conduct          = 'test.llm.conduct'
Gateway_Identity         = 'test.llm.identity'
Gateway_Sessions         = 'test.llm.sessions'
Gateway_TTL              = 'test.llm.ttl'
Gateway_Runtime          = 'test.llm.runtime'
Gateway_Docstring        = 'test.llm.docstring'
Gateway_Pipeline         = 'test.llm.pipeline'
Gateway_PII_Truncate     = 'test.llm.pii.truncate'
Gateway_Reject_Both      = 'test.llm.reject.both'
Gateway_Compact_Cap      = 'test.llm.compact.cap'
Gateway_Threshold_Low    = 'test.llm.threshold.low'
Gateway_Nulls            = 'test.llm.nulls'
Gateway_Whitespace       = 'test.llm.whitespace'
Gateway_Base64           = 'test.llm.base64'
Gateway_PII_Two_Lands    = 'test.llm.pii.two-lands'
Gateway_PII_Detector     = 'test.llm.pii.detector'
Gateway_PII_No_Validate  = 'test.llm.pii.no-validate'
Gateway_Unicode_Reject   = 'test.llm.unicode.reject'
Gateway_URL_Neutralize   = 'test.llm.url.neutralize'
Gateway_URL_Reject       = 'test.llm.url.reject'
Gateway_Audit_Off        = 'test.llm.audit.off'

Path_Main             = '/mcp/llm/main'
Path_Validate         = '/mcp/llm/validate'
Path_Skills           = '/mcp/llm/skills'
Path_Shaping_Truncate = '/mcp/llm/shaping-truncate'
Path_Shaping_Block    = '/mcp/llm/shaping-block'
Path_Shaping_Threshold = '/mcp/llm/shaping-threshold'
Path_Shaping_Wide     = '/mcp/llm/shaping-wide'
Path_Shaping_Narrow   = '/mcp/llm/shaping-narrow'
Path_Compaction       = '/mcp/llm/compaction'
Path_PII              = '/mcp/llm/pii'
Path_PII_Exclude      = '/mcp/llm/pii-exclude'
Path_PII_Other_Land   = '/mcp/llm/pii-other-land'
Path_Safety           = '/mcp/llm/safety'
Path_Safety_Reject    = '/mcp/llm/safety-reject'
Path_Filters          = '/mcp/llm/filters'
Path_Lifecycle        = '/mcp/llm/lifecycle'
Path_Hotdeploy        = '/mcp/llm/hotdeploy'

# The isolation pair shares a URL path prefix on purpose - routing must still keep them apart
Path_Iso_A = '/mcp/llm/crm'
Path_Iso_B = '/mcp/llm/crm-extra'
Path_Iso_C = '/mcp/llm/iso-c'

Path_Conduct         = '/mcp/llm/conduct'
Path_Identity        = '/mcp/llm/identity'
Path_Sessions        = '/mcp/llm/sessions'
Path_TTL             = '/mcp/llm/ttl'
Path_Runtime         = '/mcp/llm/runtime'
Path_Docstring       = '/mcp/llm/docstring'
Path_Pipeline        = '/mcp/llm/pipeline'
Path_PII_Truncate    = '/mcp/llm/pii-truncate'
Path_Reject_Both     = '/mcp/llm/reject-both'
Path_Compact_Cap     = '/mcp/llm/compact-cap'
Path_Threshold_Low   = '/mcp/llm/threshold-low'
Path_Nulls           = '/mcp/llm/nulls'
Path_Whitespace      = '/mcp/llm/whitespace'
Path_Base64          = '/mcp/llm/base64'
Path_PII_Two_Lands   = '/mcp/llm/pii-two-lands'
Path_PII_Detector    = '/mcp/llm/pii-detector'
Path_PII_No_Validate = '/mcp/llm/pii-no-validate'
Path_Unicode_Reject  = '/mcp/llm/unicode-reject'
Path_URL_Neutralize  = '/mcp/llm/url-neutralize'
Path_URL_Reject      = '/mcp/llm/url-reject'
Path_Audit_Off       = '/mcp/llm/audit-off'

# ################################################################################################################################
# ################################################################################################################################

# The token cap the shaping gateways enforce and the threshold the threshold gateway skips below.
# The cap must stay at or above the minimum usable byte budget for trimming,
# which is 1000 tokens under the default four characters per token.
Shaping_Cap_Tokens    = 4000
Shaping_Threshold_Tokens = 1_000_000

# The characters-per-token ratios of the two ratio gateways - the same payload passes under
# the wide ratio and goes over the cap under the narrow one
Shaping_Ratio_Wide   = 10_000.0
Shaping_Ratio_Narrow = 1.0

# The cap of the pipeline gateways - the minimum usable byte budget for trimming,
# so the oversized roster of the pipeline tests is provably over it
Pipeline_Cap_Tokens = 1000

# The threshold of the low-threshold gateway - the oversized invoice call is provably over it
Threshold_Low_Tokens = 1000

# The session TTL of the TTL gateway, in seconds, and the reaper sweep interval
# the conftest configures the server with
Session_TTL_Seconds     = 3
Reaper_Interval_Seconds = 5

# The per-identity session cap the server enforces by default
Session_Cap = 100

# The host the safety gateways' URL policy allows
Safety_Allowed_Host = 'example.com'

# The land whose detectors the PII gateways run and one whose detectors never match the customer record
PII_Land_Main  = 'intl'
PII_Land_Other = 'de'

# The land whose detectors recognize the Japanese record's national id
PII_Land_Japan = 'jp'

# The detector the exclude gateway leaves out and the one the detector-only gateway names directly
PII_Exclude_Detector = 'intl_email'
PII_Named_Detector   = 'intl_email'

# The name of the self.llm outconn the suite creates - no tests use it yet, it is the setup for them
LLM_Outconn_Name = 'test.mcp.llm'

# ################################################################################################################################
# ################################################################################################################################
