@security-basic-auth
Feature: zato.security.basic-auth.get-list
  Returns a list of HTTP Basic Auth security definitions configured on a given cluster.

  @security.basic-auth.get-list
  Scenario: Get basic auth definitions and test that is not empty

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.basic-auth.get-list"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_security_basic_auth_get_list_response" isn't an empty list
