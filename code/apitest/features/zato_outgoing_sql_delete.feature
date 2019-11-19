@outgoing
Feature: zato.outgoing.sql.delete
  Deletes an outgoing SQL connection by its ID.


  @outgoing.sql.delete
    Scenario: Create SQL Connection
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.outgoing.sql.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/engine" in request is "postgresql"
    Given JSON Pointer "/host" in request is "localhost"
    Given JSON Pointer "/port" in request is "5432"
    Given JSON Pointer "/db_name" in request is "true"
    Given JSON Pointer "/username" in request is "anonymous"
    Given JSON Pointer "/pool_size" in request is "20"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_outgoing_sql_create_response/id" from response under "def_id"
    And JSON Pointer "/zato_outgoing_sql_create_response/id" is any integer
    And I sleep for "2"


  @outgoing.sql.delete
  Scenario: Delete created SQL connection

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.outgoing.sql.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#def_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"