@service
Feature: zato.service.has-wsdl
  Returns a boolean flag indicating whether there is a WSDL document attached to a service.

  @service-haswsdl
  Scenario: Setup
    Given I store "test-service.test-service" under "service_name"


  @service-haswsdl
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

  @service-haswsdl
  Scenario: Check that there is no wsdl attached to the service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.has-wsdl"

    Given format "JSON"
    Given request "service_set_wsdl.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#service_name"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_has_wsdl_response/has_wsdl" is False


  @service-haswsdl
  Scenario: Set WSDL to created service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.set-wsdl"

    Given format "JSON"
    Given request "service_set_wsdl.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#service_name"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @service-haswsdl
  Scenario: Check that the wsdl is now attached to the service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.has-wsdl"

    Given format "JSON"
    Given request "service_set_wsdl.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#service_name"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_has_wsdl_response/has_wsdl" is True

  @service-haswsdl
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

  @service-haswsdl
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