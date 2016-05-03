@security.tech-account
Feature: zato.security.tech-account.get-by-id
  Returns a technical account by its ID.

  @security.tech-account.get-by-id
  Scenario: Set up

    Given I store a random string under "url_path"
    Given I store a random string under "tech_name"
    Given I store a random string under "tech_password"
    Given I store a random string under "invalid_password"

  @security.tech-account.get-by-id
  Scenario: Create a new technichal account

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.tech-account.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#tech_name"
    Given JSON Pointer "/is_active" in request is "true"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_security_tech_account_create_response/name" from response under "tech_name"
    And I store "/zato_security_tech_account_create_response/id" from response under "tech_id"

    And I sleep for "1"


  @security.tech-account.get-by-id
  Scenario: Invoke zato.security.tech-account.get-by-id

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.tech-account.get-by-id"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#tech_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_security_tech_account_get_by_id_response/is_active" is True
    And JSON Pointer "/zato_security_tech_account_get_by_id_response/id" is "#tech_id"
    And JSON Pointer "/zato_security_tech_account_get_by_id_response/name" is "#tech_name"


  @security.tech-account.get-by-id
  Scenario: Delete the technical account we just used

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.security.tech-account.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#tech_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I sleep for "1"
