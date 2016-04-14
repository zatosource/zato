@service
Feature: zato.service.upload-package
  Upload a service, invoke it and delete service afterwards

  @service-confreqres
  Scenario: Get current request response frecuency for zato.ping service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-request-response"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "zato.ping"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_service_request_response_response/sample_req_resp_freq" from response under "sample_req_resp_freq"

  @service-confreqres
  Scenario: Configure request response for zato.ping service to store 1 request every 3 calls

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.configure-request-response"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "zato.ping"
    Given JSON Pointer "/sample_req_resp_freq" in request is "3"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @service-confreqres
  Scenario: Invoke ping service first time

      Given address "$ZATO_API_TEST_SERVER"
      Given URL path "/zato/ping"
      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/test" in request is "hola"

      When the URL is invoked

      Then JSON Pointer "/zato_ping_response/pong" is "zato"

  @service-confreqres
  Scenario: Invoke ping service second time

      Given address "$ZATO_API_TEST_SERVER"
      Given URL path "/zato/ping"
      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/test" in request is "hola"

      When the URL is invoked

      Then JSON Pointer "/zato_ping_response/pong" is "zato"

  @service-confreqres
  Scenario: Invoke ping service third time

      Given address "$ZATO_API_TEST_SERVER"
      Given URL path "/zato/ping"
      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/test" in request is "hola"

      When the URL is invoked

      Then JSON Pointer "/zato_ping_response/pong" is "zato"



  @service-confreqres
  Scenario: Get current request response frecuency and captured request

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-request-response"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "zato.ping"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_request_response_response/sample_req" is base64 JSON which pointer "/test" has "hola"
    And JSON Pointer "/zato_service_request_response_response/sample_resp" is base64 JSON which pointer "/zato_ping_response/pong" has "zato"

  @service-confreqres
  Scenario: Restore original sample_req_resp_freq

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.configure-request-response"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "zato.ping"
    Given JSON Pointer "/sample_req_resp_freq" in request is "#sample_req_resp_freq"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"