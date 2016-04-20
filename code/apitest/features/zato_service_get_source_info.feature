@service
Feature: zato.service.get-source-info
  Returns information regarding how a particular service’s source code looks like.

  @service.get-source-info
  Scenario: Get source info for zato.ping service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-source-info"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "zato.ping"
    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_service_get_source_info_response/source" isn't empty
