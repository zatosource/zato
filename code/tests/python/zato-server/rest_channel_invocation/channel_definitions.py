# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The names, paths and credentials of the objects of the suite and the enmasse YAML that creates them.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_tokens import IdentityProvider

# ################################################################################################################################
# ################################################################################################################################

class Credentials:
    Basic_Username = 'john.smith'
    Basic_Password = 'Customer.Password.1'

    Unicode_Username = 'renée.thompson'
    Unicode_Password = 'pässwörd:with:colons'

    Inactive_Username = 'robert.brown'
    Inactive_Password = 'Inactive.Password.1'

    Changing_Username = 'linda.davis'
    Changing_Password_First = 'Changing.Password.1'
    Changing_Password_Second = 'Changing.Password.2'

    API_Key = 'customer-api-key-1'
    API_Key_Custom = 'customer-api-key-2'
    API_Key_Custom_Header = 'X-Customer-Key'
    API_Key_Changing_First = 'changing-api-key-1'
    API_Key_Changing_Second = 'changing-api-key-2'

    Static_Token = 'customer-static-token-1'

    Group_Basic_Username = 'michael.wilson'
    Group_Basic_Password = 'Group.Password.1'
    Group_API_Key = 'group-api-key-1'
    Group_Extra_Username = 'jennifer.moore'
    Group_Extra_Password = 'Group.Password.2'

    Rejection_Username = 'david.taylor'
    Rejection_Password = 'Rejection.Password.1'

    Limited_Username = 'susan.anderson'
    Limited_Password = 'Limited.Password.1'

    WSS_Username = 'james.jackson'
    WSS_Password = 'WSS.Password.1'

    MTLS_Fingerprint = 'AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89'
    MTLS_Subject_DN = 'CN=customers.example.com,O=Example Corporation,C=US'

    JWT_Claim_Name = 'department'
    JWT_Claim_Value = 'accounting'

# ################################################################################################################################
# ################################################################################################################################

class Security:
    Basic = 'test.channel.sec.basic'
    Basic_Unicode = 'test.channel.sec.basic.unicode'
    Basic_Inactive = 'test.channel.sec.basic.inactive'
    Basic_Changing = 'test.channel.sec.basic.changing'
    API_Key = 'test.channel.sec.apikey'
    API_Key_Custom = 'test.channel.sec.apikey.custom'
    API_Key_Changing = 'test.channel.sec.apikey.changing'
    Bearer_Static = 'test.channel.sec.bearer.static'
    Bearer_JWT = 'test.channel.sec.bearer.jwt'
    Bearer_JWT_Claims = 'test.channel.sec.bearer.jwt.claims'
    Group_Basic = 'test.channel.sec.group.basic'
    Group_API_Key = 'test.channel.sec.group.apikey'
    Group_Extra = 'test.channel.sec.group.extra'
    Rejection = 'test.channel.sec.rejection'
    Limited = 'test.channel.sec.limited'
    MTLS_Fingerprint = 'test.channel.sec.mtls.fingerprint'
    MTLS_Subject = 'test.channel.sec.mtls.subject'
    WSS = 'test.channel.sec.wss'

class Groups:
    Customers = 'test.channel.group.customers'
    Empty = 'test.channel.group.empty'

# ################################################################################################################################
# ################################################################################################################################

class Paths:

    # URL matching and the request context
    Echo = '/test/channel/echo'
    Customer_Orders = '/test/channel/customers/{customer_id}/orders/{order_id}'
    Items_Generic = '/test/channel/items/{item_id}'
    Items_Special = '/test/channel/items/special'
    Files = '/test/channel/files/{file_path}'
    Method_GET = '/test/channel/method-get'
    Params_Path_Priority = '/test/channel/priority/path/{customer_id}'
    Params_Query_Priority = '/test/channel/priority/query/{customer_id}'
    Params_Not_Merged = '/test/channel/not-merged/{customer_id}'
    Lifecycle = '/test/channel/lifecycle'
    Lifecycle_Edited = '/test/channel/lifecycle-edited'
    Internal_Shadow = '/openapi/{name}'

    # Payloads
    Echo_XML = '/test/channel/echo-xml'
    Echo_Form = '/test/channel/echo-form'
    Echo_No_Format = '/test/channel/echo-no-format'
    Input_Declared = '/test/channel/input/declared'
    Input_Model = '/test/channel/input/model'

    # Security
    Basic = '/test/channel/security/basic'
    Basic_Unicode = '/test/channel/security/basic-unicode'
    Basic_Inactive = '/test/channel/security/basic-inactive'
    Basic_Changing = '/test/channel/security/basic-changing'
    API_Key = '/test/channel/security/apikey'
    API_Key_Custom = '/test/channel/security/apikey-custom'
    API_Key_Changing = '/test/channel/security/apikey-changing'
    Bearer_Static = '/test/channel/security/bearer-static'
    Bearer_JWT = '/test/channel/security/bearer-jwt'
    Bearer_JWT_Claims = '/test/channel/security/bearer-jwt-claims'
    Group = '/test/channel/security/group'
    Group_Empty = '/test/channel/security/group-empty'
    Rejection = '/test/channel/security/rejection'
    MTLS_Fingerprint = '/test/channel/security/mtls-fingerprint'
    MTLS_Subject = '/test/channel/security/mtls-subject'

    # Rate limiting
    Rate_Channel = '/test/channel/rate/channel'
    Rate_Disallowed = '/test/channel/rate/disallowed'
    Rate_Security = '/test/channel/rate/security'
    Rate_Changing = '/test/channel/rate/changing'

    # Responses and errors
    Response_Dict = '/test/channel/response/dict'
    Response_List = '/test/channel/response/list'
    Response_String = '/test/channel/response/string'
    Response_Bytes = '/test/channel/response/bytes'
    Response_None = '/test/channel/response/none'
    Response_Dot_Access = '/test/channel/response/dot-access'
    Response_Model = '/test/channel/response/model'
    Response_Model_List = '/test/channel/response/model-list'
    Response_Status_Headers = '/test/channel/response/status-headers'
    Response_Content_Type = '/test/channel/response/content-type'
    Response_Error_Status = '/test/channel/response/error-status'
    Response_Dict_XML = '/test/channel/response/dict-xml'
    Response_Dict_No_Format = '/test/channel/response/dict-no-format'
    Error_Exception = '/test/channel/error/exception'
    Error_Bad_Request = '/test/channel/error/bad-request'
    Error_Unauthorized = '/test/channel/error/unauthorized'
    Error_Forbidden = '/test/channel/error/forbidden'
    Error_Not_Found = '/test/channel/error/not-found'
    Error_After_Headers = '/test/channel/error/after-headers'

    # Hooks, verbs and scheduling
    Hooks = '/test/channel/hooks'
    Not_Accepted = '/test/channel/not-accepted'
    Verbs = '/test/channel/verbs'
    Sleep = '/test/channel/sleep'

    # Channel state
    Inactive = '/test/channel/state/inactive'
    Deprecated = '/test/channel/state/deprecated'

    # Audit log, response cache and queue
    Audit_Active = '/test/channel/audit/active'
    Audit_Inactive = '/test/channel/audit/inactive'
    Cached = '/test/channel/cached'

    # SOAP
    SOAP_Echo = '/test/channel/soap/echo'
    SOAP_Error = '/test/channel/soap/error'
    SOAP_Bad_Request = '/test/channel/soap/bad-request'
    SOAP_WSS = '/test/channel/soap/wss'

# ################################################################################################################################
# ################################################################################################################################

class Channels:
    Echo = 'test.channel.echo'
    Customer_Orders = 'test.channel.customer-orders'
    Lifecycle = 'test.channel.lifecycle'
    Audit_Active = 'test.channel.audit.active'
    Audit_Inactive = 'test.channel.audit.inactive'
    Deprecated = 'test.channel.state.deprecated'
    Basic = 'test.channel.security.basic'
    Bearer_JWT = 'test.channel.security.bearer-jwt'
    SOAP_Echo = 'test.channel.soap.echo'
    Rate_Channel = 'test.channel.rate.channel'

class Services:
    Echo = 'test.channel.echo'
    Ping = 'test.channel.ping'

# ################################################################################################################################
# ################################################################################################################################

class Limits:
    Refill_Rate = 1
    Window_Limit = 10_000
    Channel_Burst = 2
    Security_Burst = 3
    Changing_First = 2
    Changing_Second = 6

class Deprecation:
    Sunset = '2027-06-30'
    Successor = '/test/channel/v2/customers'

# ################################################################################################################################
# ################################################################################################################################

def _rate_limiting(burst:'int', disallowed:'bool' = False) -> 'str':
    """ Returns the YAML of a rate limiting rule that applies to every address all day. The token bucket
    admits a burst of requests and then one request per second, and the fixed window stays above it.
    """
    disallowed_value = 'true' if disallowed else 'false'

    out = f"""
    rate_limiting:
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            disabled: false
            disallowed: {disallowed_value}
            rate: {Limits.Refill_Rate}
            burst: {burst}
            limit: {Limits.Window_Limit}
            limit_unit: minute"""

    return out

# ################################################################################################################################

def _channel(
    name:'str',
    service:'str',
    url_path:'str',
    *,
    data_format:'str' = 'json',
    extra:'str' = '',
    ) -> 'str':
    """ Returns the YAML of one REST channel.
    """
    out = f"""
  - name: {name}
    service: {service}
    url_path: {url_path}
    is_audit_log_active: false"""

    if data_format:
        out += f"""
    data_format: {data_format}"""

    out += extra

    return out

# ################################################################################################################################

def build_security_yaml(
    provider:'IdentityProvider',
    *,
    basic_changing_password:'str' = Credentials.Changing_Password_First,
    api_key_changing:'str' = Credentials.API_Key_Changing_First,
    group_members:'tuple[str, ...]' = (Security.Group_Basic, Security.Group_API_Key),
    ) -> 'str':
    """ Returns the YAML of the security definitions and the security groups of the suite.
    """
    members = ''
    for member in group_members:
        members += f"""
      - {member}"""

    out = f"""
security:
  - name: {Security.Basic}
    type: basic_auth
    username: {Credentials.Basic_Username}
    password: "{Credentials.Basic_Password}"
  - name: {Security.Basic_Unicode}
    type: basic_auth
    username: "{Credentials.Unicode_Username}"
    password: "{Credentials.Unicode_Password}"
  - name: {Security.Basic_Inactive}
    type: basic_auth
    username: {Credentials.Inactive_Username}
    password: "{Credentials.Inactive_Password}"
    is_active: false
  - name: {Security.Basic_Changing}
    type: basic_auth
    username: {Credentials.Changing_Username}
    password: "{basic_changing_password}"
  - name: {Security.API_Key}
    type: apikey
    password: "{Credentials.API_Key}"
  - name: {Security.API_Key_Custom}
    type: apikey
    header: {Credentials.API_Key_Custom_Header}
    password: "{Credentials.API_Key_Custom}"
  - name: {Security.API_Key_Changing}
    type: apikey
    password: "{api_key_changing}"
  - name: {Security.Bearer_Static}
    type: bearer_token
    static_token: "{Credentials.Static_Token}"
  - name: {Security.Bearer_JWT}
    type: bearer_token
    username: test.channel.jwt.client
    password: Customer.Client.Secret.1
    issuer: {provider.issuer}
    audience: {provider.audience}
    jwks_url: {provider.jwks_url}
  - name: {Security.Bearer_JWT_Claims}
    type: bearer_token
    username: test.channel.jwt.claims.client
    password: Customer.Client.Secret.2
    issuer: {provider.issuer}
    audience: {provider.audience}
    jwks_url: {provider.jwks_url}
    claims:
      - {Credentials.JWT_Claim_Name}={Credentials.JWT_Claim_Value}
  - name: {Security.Group_Basic}
    type: basic_auth
    username: {Credentials.Group_Basic_Username}
    password: "{Credentials.Group_Basic_Password}"
  - name: {Security.Group_API_Key}
    type: apikey
    password: "{Credentials.Group_API_Key}"
  - name: {Security.Group_Extra}
    type: basic_auth
    username: {Credentials.Group_Extra_Username}
    password: "{Credentials.Group_Extra_Password}"
  - name: {Security.Rejection}
    type: basic_auth
    username: {Credentials.Rejection_Username}
    password: "{Credentials.Rejection_Password}"
  - name: {Security.Limited}
    type: basic_auth
    username: {Credentials.Limited_Username}
    password: "{Credentials.Limited_Password}"{_rate_limiting(Limits.Security_Burst)}
  - name: {Security.MTLS_Fingerprint}
    type: mtls
    client_cert_fingerprint: "{Credentials.MTLS_Fingerprint}"
  - name: {Security.MTLS_Subject}
    type: mtls
    client_cert_subject_dn: "{Credentials.MTLS_Subject_DN}"
  - name: {Security.WSS}
    type: wss
    username: {Credentials.WSS_Username}
    password: "{Credentials.WSS_Password}"
    mode: username_token
    use_digest: false

groups:
  - name: {Groups.Customers}
    members:{members}
  - name: {Groups.Empty}
    members: []
"""

    return out

# ################################################################################################################################

def build_channel_yaml(
    *,
    lifecycle_path:'str' = Paths.Lifecycle,
    lifecycle_service:'str' = Services.Echo,
    rate_changing:'int' = Limits.Changing_First,
    ) -> 'str':
    """ Returns the YAML of the REST and SOAP channels of the suite.
    """
    out = 'channel_rest:'

    # URL matching and the request context
    out += _channel(Channels.Echo, Services.Echo, Paths.Echo)
    out += _channel(Channels.Customer_Orders, Services.Echo, Paths.Customer_Orders)
    out += _channel('test.channel.items.generic', Services.Echo, Paths.Items_Generic)
    out += _channel('test.channel.items.special', Services.Ping, Paths.Items_Special)
    out += _channel('test.channel.files', Services.Echo, Paths.Files)
    out += _channel('test.channel.method-get', Services.Echo, Paths.Method_GET, extra="""
    method: GET""")
    out += _channel('test.channel.priority.path', Services.Echo, Paths.Params_Path_Priority, extra="""
    url_params_pri: path-over-qs""")
    out += _channel('test.channel.priority.query', Services.Echo, Paths.Params_Query_Priority, extra="""
    url_params_pri: qs-over-path""")
    out += _channel('test.channel.not-merged', Services.Echo, Paths.Params_Not_Merged, extra="""
    merge_url_params_req: false""")
    out += _channel(Channels.Lifecycle, lifecycle_service, lifecycle_path)
    out += _channel('test.channel.internal-shadow', Services.Ping, Paths.Internal_Shadow)

    # Payloads
    out += _channel('test.channel.echo-xml', Services.Echo, Paths.Echo_XML, data_format='xml')
    out += _channel('test.channel.echo-form', Services.Echo, Paths.Echo_Form, data_format='form')
    out += _channel('test.channel.echo-no-format', Services.Echo, Paths.Echo_No_Format, data_format='')
    out += _channel('test.channel.input.declared', 'test.channel.input.declared', Paths.Input_Declared)
    out += _channel('test.channel.input.model', 'test.channel.input.model', Paths.Input_Model)

    # Security
    out += _channel(Channels.Basic, Services.Echo, Paths.Basic, extra=f"""
    security: {Security.Basic}""")
    out += _channel('test.channel.security.basic-unicode', Services.Echo, Paths.Basic_Unicode, extra=f"""
    security: {Security.Basic_Unicode}""")
    out += _channel('test.channel.security.basic-inactive', Services.Echo, Paths.Basic_Inactive, extra=f"""
    security: {Security.Basic_Inactive}""")
    out += _channel('test.channel.security.basic-changing', Services.Echo, Paths.Basic_Changing, extra=f"""
    security: {Security.Basic_Changing}""")
    out += _channel('test.channel.security.apikey', Services.Echo, Paths.API_Key, extra=f"""
    security: {Security.API_Key}""")
    out += _channel('test.channel.security.apikey-custom', Services.Echo, Paths.API_Key_Custom, extra=f"""
    security: {Security.API_Key_Custom}""")
    out += _channel('test.channel.security.apikey-changing', Services.Echo, Paths.API_Key_Changing, extra=f"""
    security: {Security.API_Key_Changing}""")
    out += _channel('test.channel.security.bearer-static', Services.Echo, Paths.Bearer_Static, extra=f"""
    security: {Security.Bearer_Static}""")
    out += _channel(Channels.Bearer_JWT, Services.Echo, Paths.Bearer_JWT, extra=f"""
    security: {Security.Bearer_JWT}""")
    out += _channel('test.channel.security.bearer-jwt-claims', Services.Echo, Paths.Bearer_JWT_Claims, extra=f"""
    security: {Security.Bearer_JWT_Claims}""")
    out += _channel('test.channel.security.group', Services.Echo, Paths.Group, extra=f"""
    groups:
      - {Groups.Customers}""")
    out += _channel('test.channel.security.group-empty', Services.Echo, Paths.Group_Empty, extra=f"""
    groups:
      - {Groups.Empty}""")
    out += _channel('test.channel.security.rejection', 'test.channel.auth-rejection', Paths.Rejection, extra=f"""
    security: {Security.Rejection}""")
    out += _channel('test.channel.security.mtls-fingerprint', Services.Echo, Paths.MTLS_Fingerprint, extra=f"""
    security: {Security.MTLS_Fingerprint}""")
    out += _channel('test.channel.security.mtls-subject', Services.Echo, Paths.MTLS_Subject, extra=f"""
    security: {Security.MTLS_Subject}""")

    # Rate limiting
    out += _channel(Channels.Rate_Channel, Services.Ping, Paths.Rate_Channel,
        extra=_rate_limiting(Limits.Channel_Burst))
    out += _channel('test.channel.rate.disallowed', Services.Echo, Paths.Rate_Disallowed,
        extra=_rate_limiting(Limits.Channel_Burst, disallowed=True))
    out += _channel('test.channel.rate.security', Services.Ping, Paths.Rate_Security, extra=f"""
    security: {Security.Limited}""")
    out += _channel('test.channel.rate.changing', Services.Ping, Paths.Rate_Changing,
        extra=_rate_limiting(rate_changing))

    # Responses and errors
    out += _channel('test.channel.response.dict', 'test.channel.response.dict', Paths.Response_Dict)
    out += _channel('test.channel.response.list', 'test.channel.response.list', Paths.Response_List)
    out += _channel('test.channel.response.string', 'test.channel.response.string', Paths.Response_String)
    out += _channel('test.channel.response.bytes', 'test.channel.response.bytes', Paths.Response_Bytes)
    out += _channel('test.channel.response.none', 'test.channel.response.none', Paths.Response_None)
    out += _channel('test.channel.response.dot-access', 'test.channel.response.dot-access', Paths.Response_Dot_Access)
    out += _channel('test.channel.response.model', 'test.channel.response.model', Paths.Response_Model)
    out += _channel('test.channel.response.model-list', 'test.channel.response.model-list', Paths.Response_Model_List)
    out += _channel('test.channel.response.status-headers', 'test.channel.response.status-headers',
        Paths.Response_Status_Headers)
    out += _channel('test.channel.response.content-type', 'test.channel.response.content-type', Paths.Response_Content_Type)
    out += _channel('test.channel.response.error-status', 'test.channel.response.error-status', Paths.Response_Error_Status)
    out += _channel('test.channel.response.dict-xml', 'test.channel.response.dict', Paths.Response_Dict_XML,
        data_format='xml')
    out += _channel('test.channel.response.dict-no-format', 'test.channel.response.dict', Paths.Response_Dict_No_Format,
        data_format='')
    out += _channel('test.channel.error.exception', 'test.channel.error.exception', Paths.Error_Exception)
    out += _channel('test.channel.error.bad-request', 'test.channel.error.bad-request', Paths.Error_Bad_Request)
    out += _channel('test.channel.error.unauthorized', 'test.channel.error.unauthorized', Paths.Error_Unauthorized)
    out += _channel('test.channel.error.forbidden', 'test.channel.error.forbidden', Paths.Error_Forbidden)
    out += _channel('test.channel.error.not-found', 'test.channel.error.not-found', Paths.Error_Not_Found)
    out += _channel('test.channel.error.after-headers', 'test.channel.error.after-headers', Paths.Error_After_Headers)

    # Hooks, verbs and scheduling
    out += _channel('test.channel.hooks', 'test.channel.hooks', Paths.Hooks)
    out += _channel('test.channel.not-accepted', 'test.channel.not-accepted', Paths.Not_Accepted)
    out += _channel('test.channel.verbs', 'test.channel.verbs', Paths.Verbs)
    out += _channel('test.channel.sleep', 'test.channel.sleep', Paths.Sleep)

    # Channel state
    out += _channel('test.channel.state.inactive', Services.Echo, Paths.Inactive, extra="""
    is_active: false""")
    out += _channel(Channels.Deprecated, Services.Echo, Paths.Deprecated, extra=f"""
    is_deprecated: true
    deprecation_sunset: "{Deprecation.Sunset}"
    deprecation_successor: "{Deprecation.Successor}\"""")

    # Audit log and response cache
    out += _channel(Channels.Audit_Active, Services.Echo, Paths.Audit_Active, extra="""
    is_audit_log_active: true""")
    out += _channel(Channels.Audit_Inactive, Services.Echo, Paths.Audit_Inactive)
    out += _channel('test.channel.cached', Services.Echo, Paths.Cached, extra="""
    response_cache:
      is_enabled: true
      ttl: 60
      ttl_unit: seconds
      cache_on_second_request: false""")

    # SOAP
    out += f"""

channel_soap:
  - name: {Channels.SOAP_Echo}
    service: test.channel.soap.echo
    url_path: {Paths.SOAP_Echo}
    is_audit_log_active: false
  - name: test.channel.soap.error
    service: test.channel.soap.error
    url_path: {Paths.SOAP_Error}
    is_audit_log_active: false
  - name: test.channel.soap.bad-request
    service: test.channel.soap.bad-request
    url_path: {Paths.SOAP_Bad_Request}
    is_audit_log_active: false
  - name: test.channel.soap.wss
    service: test.channel.soap.echo
    url_path: {Paths.SOAP_WSS}
    security: {Security.WSS}
    is_audit_log_active: false
"""

    return out

# ################################################################################################################################

def build_yaml(
    provider:'IdentityProvider',
    *,
    basic_changing_password:'str' = Credentials.Changing_Password_First,
    api_key_changing:'str' = Credentials.API_Key_Changing_First,
    group_members:'tuple[str, ...]' = (Security.Group_Basic, Security.Group_API_Key),
    lifecycle_path:'str' = Paths.Lifecycle,
    lifecycle_service:'str' = Services.Echo,
    rate_changing:'int' = Limits.Changing_First,
    ) -> 'str':
    """ Returns the complete enmasse YAML of the suite.
    """
    security_yaml = build_security_yaml(
        provider,
        basic_changing_password=basic_changing_password,
        api_key_changing=api_key_changing,
        group_members=group_members,
    )

    channel_yaml = build_channel_yaml(
        lifecycle_path=lifecycle_path,
        lifecycle_service=lifecycle_service,
        rate_changing=rate_changing,
    )

    out = security_yaml + '\n' + channel_yaml
    return out

# ################################################################################################################################
# ################################################################################################################################
