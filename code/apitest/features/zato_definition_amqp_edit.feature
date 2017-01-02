@definition
Feature: zato.definition.amqp.edit
  Updates an AMQP connection definition. A connection definition holds information on how to connect to a particular
  AMQP broker. Any channels using this definition will be restarted with new values.

  @definition.amqp.edit
  Scenario: Create amqp definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.amqp.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/host" in request is "localhost"
    Given JSON Pointer "/port" in request is "5672"
    Given JSON Pointer "/vhost" in request is "/dev"
    Given JSON Pointer "/username" in request is "test_user"
    Given JSON Pointer "/frame_max" in request is "131072"
    Given JSON Pointer "/heartbeat" in request is "0"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_definition_amqp_create_response/id" from response under "amqp_def_id"
    And JSON Pointer "/zato_definition_amqp_create_response/id" is any integer
    And I sleep for "2"

  @definition.amqp.edit
  Scenario: Edit amqp definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.amqp.edit"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/id" in request is "#amqp_def_id"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/host" in request is "localhost"
    Given JSON Pointer "/port" in request is "5672"
    Given JSON Pointer "/vhost" in request is "/dev"
    Given JSON Pointer "/username" in request is "test_user"
    Given JSON Pointer "/frame_max" in request is "131072"
    Given JSON Pointer "/heartbeat" in request is "0"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_definition_amqp_edit_response/id" from response under "amqp_def_id"
    And JSON Pointer "/zato_definition_amqp_edit_response/id" is any integer

  @definition.amqp.edit
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


