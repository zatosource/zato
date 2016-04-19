@service
Feature: zato.service.get-wsdl
  Returns a WSDL document attached to a service.

  @service-getwsdl
  Scenario: Setup
    Given I store "test-service.test-service" under "service_name"


  @service-getwsdl
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


  @service-getwsdl
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

  @service-getwsdl
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

  @service-getwsdl
  Scenario: Returns a WSDL document attached to a service.

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-wsdl"

    Given format "JSON"
    Given request "service_set_wsdl.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/service" in request is "#service_name"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_get_wsdl_response/wsdl" isn't empty
    And JSON Pointer "/zato_service_get_wsdl_response/wsdl_name" is "test-service.wsdl"


  @service-getwsdl
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

  @service-getwsdl
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