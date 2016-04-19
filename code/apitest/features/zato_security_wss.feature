@wss-auth
Feature: zato.security.wss.*

  @security
  @wss-create
  Scenario: Set up

    Given I store a random string under "url_path"
    Given I store a random string under "wss_name"
    Given I store a random string under "wss_username"
    Given I store a random string under "wss_password"
    Given I store a random string under "invalid_password"


  @security
  @wss-create
  Scenario: Invoke zato.security.wss.create

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#wss_name"
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/username" in request is "#wss_username"
    Given JSON Pointer "/password_type" in request is "clear_text"
    Given JSON Pointer "/reject_empty_nonce_creat" in request is "true"
    Given JSON Pointer "/reject_stale_tokens" in request is "true"
    Given JSON Pointer "/reject_expiry_limit" in request is "15"
    Given JSON Pointer "/nonce_freshness_time" in request is "15"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_security_wss_create_response/name" from response under "wss_name"
    And I store "/zato_security_wss_create_response/id" from response under "wss_id"


  @security
  @wss-create
  Scenario: Invoke zato.security.wss.change-password

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.change-password"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#wss_id"
    Given JSON Pointer "/password1" in request is "#wss_password"
    Given JSON Pointer "/password2" in request is "#wss_password"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"



  @security
  @wss-create
  Scenario: Prepare params for ping
    Given I store UTC now under "soap_created" "default"
    Given I store a format string "{soap_created}.000Z" under "soap_created_value"

  @security
  @wss-create
  Scenario: Create HTTP channel for zato.ping service to be executed with the security definition created

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"


    Given URL path "/zato/json/zato.http-soap.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/connection" in request is "channel"
    Given JSON Pointer "/transport" in request is "soap"
    Given JSON Pointer "/is_internal" in request is "false"
    Given JSON Pointer "/url_path" in request is "/apitest/security/wss/ping"
    Given JSON Pointer "/service" in request is "zato.ping"
    Given JSON Pointer "/data_format" in request is "xml"
    Given JSON Pointer "/method" in request is "GET"
    Given JSON Pointer "/security_id" in request is "#wss_id"

    When the URL is invoked

    Then status is "200"
    And I store "/zato_http_soap_create_response/name" from response under "ping_channel_name"
    And I store "/zato_http_soap_create_response/id" from response under "ping_channel_id"



  @security
  @wss-chann
  Scenario: Invoke to fail zato.ping over the previusly created http channel with invalid Created value

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/security/wss/ping"

    Given format "XML"
    Given request "security_wss_invoke_service.xml"
    Given namespace prefix "soapenv" of "http://schemas.xmlsoap.org/soap/envelope/"
    Given namespace prefix "zato" of "https://zato.io/ns/20130518"
    Given namespace prefix "wsse" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    Given namespace prefix "wsu" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"

    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username" in request is "#wss_username"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password" in request is "#wss_password"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce" in request is "f8nUe3YupTU5ISdCy3X9Gg=="
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created" in request is "2011-05-04T19:01:40.981Z"

    When the URL is invoked

    Then status is "401"


  @security
  @wss-chann
  Scenario: Invoke zato.ping over the previusly created http channel with valid credentials

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/security/wss/ping"

    Given format "XML"
    Given request "security_wss_invoke_service.xml"
    Given namespace prefix "soapenv" of "http://schemas.xmlsoap.org/soap/envelope/"
    Given namespace prefix "zato" of "https://zato.io/ns/20130518"
    Given namespace prefix "wsse" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    Given namespace prefix "wsu" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"

    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username" in request is "#wss_username"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password" in request is "#wss_password"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce" in request is "f8nUe3YupTU5ISdCy3X9Gg=="
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created" in request is "#soap_created_value"

    When the URL is invoked

    Then status is "200"


  @security
  @wss-chann
  Scenario: Invoke to fail zato.ping over the previusly created http channel with invalid credentials

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/security/wss/ping"

    Given format "XML"
    Given request "security_wss_invoke_service.xml"
    Given namespace prefix "soapenv" of "http://schemas.xmlsoap.org/soap/envelope/"
    Given namespace prefix "zato" of "https://zato.io/ns/20130518"
    Given namespace prefix "wsse" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    Given namespace prefix "wsu" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"

    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username" in request is "#wss_username"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password" in request is "#invalid_password"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce" in request is "f8nUe3YupTU5ISdCy3X9Gg=="
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created" in request is "#soap_created_value"

    When the URL is invoked

    Then status is "401"


  @security
  @wss-chann
  Scenario: Invoke to fail zato.ping over the previusly created http channel with empty created value

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/security/wss/ping"

    Given format "XML"
    Given request "security_wss_invoke_service.xml"
    Given namespace prefix "soapenv" of "http://schemas.xmlsoap.org/soap/envelope/"
    Given namespace prefix "zato" of "https://zato.io/ns/20130518"
    Given namespace prefix "wsse" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    Given namespace prefix "wsu" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"

    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username" in request is "#wss_username"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password" in request is "#invalid_password"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce" in request is "f8nUe3YupTU5ISdCy3X9Gg=="

    When the URL is invoked

    Then status is "401"


  @security
  @wss-chann
  Scenario: Invoke zato.security.wss.edit with random data to test that it cannot login

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.edit"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/id" in request is "#wss_id"
    Given JSON Pointer "/name" in request is "#wss_name"
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/username" in request is "#wss_username"
    Given JSON Pointer "/password_type" in request is "clear_text"
    Given JSON Pointer "/reject_empty_nonce_creat" in request is "false"
    Given JSON Pointer "/reject_stale_tokens" in request is "false"
    Given JSON Pointer "/reject_expiry_limit" in request is "15"
    Given JSON Pointer "/nonce_freshness_time" in request is "15"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_security_wss_edit_response/name" from response under "wss_edit_name"


  @security
  @wss-chann
  Scenario: Invoke zato.ping over the previusly created http channel with empty nonce & created value and valid credentials

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/security/wss/ping"

    Given format "XML"
    Given request "security_wss_invoke_service.xml"
    Given namespace prefix "soapenv" of "http://schemas.xmlsoap.org/soap/envelope/"
    Given namespace prefix "zato" of "https://zato.io/ns/20130518"
    Given namespace prefix "wsse" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    Given namespace prefix "wsu" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"

    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username" in request is "#wss_username"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password" in request is "#wss_password"
    Given XPath "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created" in request is "2011-05-04T19:01:40.981Z"

    When the URL is invoked

    Then status is "200"



  @security
  @wss-chann
  Scenario: Invoke zato.security.wss.get-list

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.get-list"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


  @security
  @wss-delete
  Scenario: Delete created HTTP channel for zato.ping

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#ping_channel_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"



  @security
  @wss-delete
  Scenario: Invoke zato.security.wss.delete

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#wss_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

