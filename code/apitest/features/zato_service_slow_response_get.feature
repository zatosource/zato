@service
Feature: zato.service.slow-response.get
  Returns details of a particular slow response by its CID and a service name.

  @service.slow-response.get
  Scenario: Setup
    Given I store "/apitest/service/testslow" under "test_url_path"
    Given I store "slow-service.slow-service" under "service_name"
    Given I store "100" under "slow_threshold"

  @service.slow-response.get
  Scenario: Upload package

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request "service_slow.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And I sleep for "1"

  @service.slow-response.get
  Scenario: Get service by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-by-name"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#service_name"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_service_get_by_name_response/name" is "#service_name"
    And I store "/zato_service_get_by_name_response/id" from response under "service_id"

  @service.slow-response.get
  Scenario: Edit service to set the slow threshold to 100

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.edit"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#service_id"
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/slow_threshold" in request is "#slow_threshold"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_edit_response/name" is "#service_name"
    And I sleep for "1"

  @service.slow-response.get
  Scenario: Invoke slow service by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.invoke"

    Given format "JSON"
    Given request "service_upload.json"
    Given JSON Pointer "/name" in request is "#service_name"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_env/cid" from response under "service_cid"

  @service.slow-response.get
  Scenario: Check slow response of the request we just did

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/zato/json/zato.service.slow-response.get"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cid" in request is "#service_cid"
    Given JSON Pointer "/name" in request is "#service_name"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_slow_response_get_response/proc_time" is any integer

  @service.slow-response.get
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