@outgoing
Feature: zato.outgoing.amqp.get-list
  Returns a list of outgoing AMQP connections defined on a given cluster.
  
  @outgoing.amqp.get-list
  Scenario: Set up
    Given I store "apitest.outconn" under "outconn_name"

  @outgoing.amqp.get-list
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

    And I store "/zato_definition_amqp_create_response/id" from response under "def_id"
    And JSON Pointer "/zato_definition_amqp_create_response/id" is any integer
    And I sleep for "2"


  @outgoing.amqp.get-list
  Scenario: Create outgoing amqp connection

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.outgoing.amqp.create"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is a random string
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/def_id" in request is "#def_id"
      Given JSON Pointer "/delivery_mode" in request is "1"
      Given JSON Pointer "/priority" in request is "6"
      Given JSON Pointer "/content_type" in request is "application/xml"
      Given JSON Pointer "/content_encoding" in request is "utf-8"
      Given JSON Pointer "/expiration" in request is "3000"
      Given JSON Pointer "/user_id" in request is a random string
      Given JSON Pointer "/app_id" in request is "ESB"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_outgoing_amqp_create_response/name" from response under "amqp_conn_name"
      And I store "/zato_outgoing_amqp_create_response/id" from response under "amqp_conn_id"
      And I sleep for "1"

  @outgoing.amqp.get-list
  Scenario: Get AMQP connections

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.outgoing.amqp.get-list"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "#amqp_conn_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_outgoing_amqp_get_list_response" isn't an empty list

  @outgoing.amqp.get-list
  Scenario: Delete created amqp outgoing connection

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.outgoing.amqp.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#amqp_conn_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @outgoing.amqp.get-list
  Scenario: Delete amqp definition
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.definition.amqp.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#def_id"
    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
