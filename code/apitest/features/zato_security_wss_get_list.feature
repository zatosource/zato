@security.wss
Feature: zato.security.wss.get-list
  Returns a list of WS-Security definitions configured on a given cluster.

  @security.wss.get-list
  Scenario: Set up

    Given I store a random string under "wss_name"
    Given I store a random string under "wss_username"


  @security.wss.get-list
  Scenario: Create new wss security definition

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#wss_name"
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/username" in request is "#wss_username"
    Given JSON Pointer "/password_type" in request is "clear_text"
    Given JSON Pointer "/reject_empty_nonce_creat" in request is "true"
    Given JSON Pointer "/reject_stale_tokens" in request is "true"
    Given JSON Pointer "/reject_expiry_limit" in request is "15"
    Given JSON Pointer "/nonce_freshness_time" in request is "15"

    When the URL is invoked

    Then status is "200"

    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_security_wss_create_response/name" from response under "wss_name"
    And I store "/zato_security_wss_create_response/id" from response under "wss_id"


  @security.wss.get-list
  Scenario: Invoke zato.security.wss.get-list

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.get-list"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_security_wss_get_list_response" isn't an empty list

  @security.wss.get-list
  Scenario: Delete wss security definition

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.wss.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#wss_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

