@security-basic-auth
Feature: zato.security.basic-auth.create
  Allows one to create an HTTP Basic Auth definition. Its default password will be a randomly generated UUID4, use zato.security.basic-auth.change-password to change it.

  @security-basic-auth.create
  Scenario: Set up

    Given I store a random string under "url_path"
    Given I store a random string under "basic_username"
    Given I store a random string under "basic_password"

  @security-basic-auth.create
  Scenario: Invoke zato.security.basic-auth.create

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.basic-auth.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/username" in request is "#basic_username"
    Given JSON Pointer "/realm" in request is a random string

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_security_basic_auth_create_response/name" from response under "basic_name"
    And I store "/zato_security_basic_auth_create_response/id" from response under "basic_id"

    And I sleep for "1"

  @security-basic-auth.create
  Scenario: Invoke zato.security.basic-auth.change-password

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.basic-auth.change-password"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#basic_id"
    Given JSON Pointer "/password1" in request is "#basic_password"
    Given JSON Pointer "/password2" in request is "#basic_password"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I sleep for "1"

  @security-basic-auth.create
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
    Given JSON Pointer "/transport" in request is "plain_http"
    Given JSON Pointer "/is_internal" in request is "false"
    Given JSON Pointer "/url_path" in request is "/apitest/security/basic-auth/ping"
    Given JSON Pointer "/service" in request is "zato.ping"
    Given JSON Pointer "/data_format" in request is "json"
    Given JSON Pointer "/method" in request is "GET"
    Given JSON Pointer "/security_id" in request is "#basic_id"

    When the URL is invoked

    Then status is "200"
    And I store "/zato_http_soap_create_response/name" from response under "ping_channel_name"
    And I store "/zato_http_soap_create_response/id" from response under "ping_channel_id"

    And I sleep for "1"

  @security-basic-auth.create
  Scenario: Invoke zato.ping over the previusly created http channel with valid credentials

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "#basic_username" "#basic_password"

    Given URL path "/apitest/security/basic-auth/ping"

    Given format "JSON"
    Given request is "{}"

    When the URL is invoked

    Then status is "200"

    Then JSON Pointer "/zato_ping_response/pong" is "zato"

  @security-basic-auth.create
  Scenario: Invoke to fail zato.ping over the previusly created http channel with invalid credentials

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "#basic_username" "failed password"

    Given URL path "/apitest/security/basic-auth/ping"

    Given format "JSON"
    Given request is "{}"

    When the URL is invoked

    Then status is "401"
    And JSON Pointer "/zato_env/result" is "ZATO_ERROR"

  @security-basic-auth.create
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

  @security-basic-auth.create
  Scenario: Delete created zato.security.basic-auth and http channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.basic-auth.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#basic_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"