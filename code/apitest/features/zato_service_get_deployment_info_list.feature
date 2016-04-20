@service
Feature: zato.service.get-deployment-info-list
  Returns information regarding where, on what servers, a given service is deployed.

  @service.get-deployment-info-list
  Scenario: Get service by name

    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"
    Given address "$ZATO_API_TEST_SERVER"
    Given URL path "/zato/json/zato.service.get-by-name"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "zato.ping"

    When the URL is invoked

    Then status is "200"
    And I store "/zato_service_get_by_name_response/id" from response under "service_id"


  @service.get-deployment-info-list
  Scenario: Get deployment info list

    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"
    Given address "$ZATO_API_TEST_SERVER"
    Given URL path "/zato/json/zato.service.get-deployment-info-list"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_get_deployment_info_list_response" isn't empty

