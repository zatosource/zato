@http-soap
Feature: zato.http-soap.edit
  Updates an already existing plain HTTP or SOAP object, which can be either channel or an outgoing connection, depending on the value of the ‘connection’ parameter.


### Test Create HTTP Connections that accept JSON ###

  @http-soap.edit
  Scenario: Create JSON HTTP channel for zato.ping

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
      Given JSON Pointer "/url_path" in request is "/apitest/httpcreate/test"
      Given JSON Pointer "/service" in request is "zato.ping"
      Given JSON Pointer "/data_format" in request is "json"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "service_channel_name"
      And I store "/zato_http_soap_create_response/id" from response under "service_channel_id"
      And I sleep for "1"


  @http-soap.edit
  Scenario: Invoke zato.ping through created http channel using JSON

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/httpcreate/test"

    Given format "JSON"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON pointer "/zato_ping_response/pong" is "zato"

  @http-soap.edit
  Scenario: Edit previously created HTTP channel for zato.ping service

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.http-soap.edit"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/id" in request is "#service_channel_id"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is a random string
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/connection" in request is "channel"
      Given JSON Pointer "/transport" in request is "plain_http"
      Given JSON Pointer "/is_internal" in request is "false"
      Given JSON Pointer "/service" in request is "zato.ping"
      Given JSON Pointer "/url_path" in request is "/apitest/httpcreate/test-edit"
      Given JSON Pointer "/data_format" in request is "json"

      When the URL is invoked

      Then status is "200"
      And JSON Pointer "/zato_env/result" is "ZATO_OK"
      And JSON pointer "/zato_http_soap_edit_response/id" is any integer
      And I sleep for "1"

  @http-soap.edit
  Scenario: Invoke edited http channel using JSON

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/httpcreate/test-edit"

    Given format "JSON"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON pointer "/zato_ping_response/pong" is "zato"


  @http-soap.edit
  Scenario: Delete created HTTP channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#service_channel_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

