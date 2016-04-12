@service
Feature: zato.service.*
  # This feature tests all the endpoints for the public api, regarding zato.service

  Scenario: upload package

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request "service_upload.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"


  Scenario: get service by name

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