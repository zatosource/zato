@definition
Feature: zato.definition.amqp.get-by-id
  Returns details regarding a particular AMQP connection definition.

  @definition.amqp.get-by-id
  Scenario: Setup
    Given I store a random string under "def_name"

  @definition.amqp.get-by-id
  Scenario: Create amqp definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.amqp.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "#def_name"
    Given JSON Pointer "/host" in request is "localhost"
    Given JSON Pointer "/port" in request is "5672"
    Given JSON Pointer "/vhost" in request is "/dev"
    Given JSON Pointer "/username" in request is "test_user"
    Given JSON Pointer "/frame_max" in request is "131072"
    Given JSON Pointer "/heartbeat" in request is "15"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_definition_amqp_create_response/id" from response under "amqp_def_id"
    And JSON Pointer "/zato_definition_amqp_create_response/id" is any integer
    And I sleep for "2"

  @definition.amqp.get-by-id
  Scenario: Get amqp definition by id
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.amqp.get-by-id"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/id" in request is "#amqp_def_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And JSON Pointer "/zato_definition_amqp_get_by_id_response/name" is "#def_name"
    And JSON Pointer "/zato_definition_amqp_get_by_id_response/host" is "localhost"
    And JSON Pointer "/zato_definition_amqp_get_by_id_response/port" is an integer "5672"
    And JSON Pointer "/zato_definition_amqp_get_by_id_response/vhost" is "/dev"
    And JSON Pointer "/zato_definition_amqp_get_by_id_response/username" is "test_user"
    And JSON Pointer "/zato_definition_amqp_get_by_id_response/frame_max" is an integer "131072"
    And JSON Pointer "/zato_definition_amqp_get_by_id_response/heartbeat" is an integer "15"

  @definition.amqp.get-by-id
  Scenario: Delete amqp definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.amqp.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#amqp_def_id"
    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


