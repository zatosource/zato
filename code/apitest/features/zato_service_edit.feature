@service
Feature: zato.service.edit
  Updates an already existing service.

  @service.edit
  Scenario: Upload package

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request "service_upload.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And I sleep for "1"

  @service.edit
  Scenario: Get service by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-by-name"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "test-service.test-service"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_service_get_by_name_response/name" is "test-service.test-service"
    And I store "/zato_service_get_by_name_response/id" from response under "service_id"

  @service.edit
  Scenario: Invoke service by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.invoke"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/name" in request is "test-service.test-service"
    # payload sent as base64 {"service_request": "hola"}
    Given JSON Pointer "/payload" in request is "eyJzZXJ2aWNlX3JlcXVlc3QiOiAiaG9sYSJ9Cg=="
    Given JSON Pointer "/data_format" in request is "json"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_invoke_response/response" is base64 JSON which pointer "/response/service_response/echo_request" has "hola"

  @service.edit
  Scenario: Create HTTP channel for test-service.test-service

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
      Given JSON Pointer "/url_path" in request is "/apitest/service/test"
      Given JSON Pointer "/service" in request is "test-service.test-service"
      Given JSON Pointer "/data_format" in request is "json"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "service_channel_name"
      And I store "/zato_http_soap_create_response/id" from response under "service_channel_id"
      And I sleep for "1"

  @service.edit
  Scenario: Edit service setting the active flag to false

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.edit"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#service_id"
    Given JSON Pointer "/is_active" in request is "false"
    Given JSON Pointer "/slow_threshold" in request is "500"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_edit_response/name" is "test-service.test-service"
    And I sleep for "1"

  @service.edit
  Scenario: Invoke service again to test that it was actually disabled

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.invoke"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/name" in request is "test-service.test-service"
    # payload sent as base64 {"service_request": "hola"}
    Given JSON Pointer "/payload" in request is "eyJzZXJ2aWNlX3JlcXVlc3QiOiAiaG9sYSJ9Cg=="
    Given JSON Pointer "/data_format" in request is "json"
    When the URL is invoked

    Then status is "500"

  @service.edit
  Scenario: Invoke service through http channel to test that it was actually disabled

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/service/test"

    Given format "JSON"
    Given request "service_upload.json"
    Given JSON Pointer "/service_request" in request is "hola"

    When the URL is invoked

    Then status is "500"


  @service.edit
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


  @service.edit
  Scenario: Delete test service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
