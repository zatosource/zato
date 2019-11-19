@definition
Feature: zato.definition.jms-wmq.edit
  Updates an IBM MQ MQ connection definition. Any channels using this definition will be restarted with new values.

  @definition.jms-wmq.edit
  Scenario: Create jms-wmq definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.jms-wmq.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/host" in request is "localhost"
    Given JSON Pointer "/port" in request is "1414"
    Given JSON Pointer "/queue_manager" in request is "QM01"
    Given JSON Pointer "/channel" in request is "ESB.PORTAL.3"
    Given JSON Pointer "/cache_open_send_queues" in request is "true"
    Given JSON Pointer "/cache_open_receive_queues" in request is "true"
    Given JSON Pointer "/use_shared_connections" in request is "true"
    Given JSON Pointer "/ssl" in request is "false"
    Given JSON Pointer "/needs_mcd" in request is "false"
    Given JSON Pointer "/max_chars_printed" in request is "200"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_definition_jms_wmq_create_response/id" from response under "def_id"
    And JSON Pointer "/zato_definition_jms_wmq_create_response/id" is any integer
    And I sleep for "2"


  @definition.jms-wmq.edit
  Scenario: Edit jms-wmq definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.jms-wmq.edit"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#def_id"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/host" in request is "localhost"
    Given JSON Pointer "/port" in request is "1414"
    Given JSON Pointer "/queue_manager" in request is "QM02"
    Given JSON Pointer "/channel" in request is "ESB.PORTAL.5"
    Given JSON Pointer "/cache_open_send_queues" in request is "true"
    Given JSON Pointer "/cache_open_receive_queues" in request is "true"
    Given JSON Pointer "/use_shared_connections" in request is "true"
    Given JSON Pointer "/ssl" in request is "false"
    Given JSON Pointer "/needs_mcd" in request is "false"
    Given JSON Pointer "/max_chars_printed" in request is "200"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_definition_jms_wmq_edit_response/id" from response under "def_id"
    And JSON Pointer "/zato_definition_jms_wmq_edit_response/id" is any integer


  @definition.jms-wmq.edit
  Scenario: Delete jms-wmq definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.jms-wmq.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#def_id"
    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


