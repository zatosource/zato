@outgoing
Feature: zato.outgoing.zmq.edit
  Updates an existing ZeroMQ outgoing connection. The connection will be stopped. If ‘is_active’ flag is ‘true’, 
  the underlying ZeroMQ socket will then be started.

  @outgoing.zmq.edit
    Scenario: Create a ZMQ Connection
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.outgoing.zmq.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/address" in request is "tcp://localhost:5555"
    Given JSON Pointer "/socket_type" in request is "PUSH"
    Given JSON Pointer "/socket_method" in request is "Bind"


    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_outgoing_zmq_create_response/id" from response under "def_id"
    And JSON Pointer "/zato_outgoing_zmq_create_response/id" is any integer
    And I sleep for "2"


  @outgoing.zmq.edit
    Scenario: Edit the ZMQ Connection
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.outgoing.zmq.edit"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#def_id"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "false"
    Given JSON Pointer "/address" in request is "tcp://localhost:5556"
    Given JSON Pointer "/socket_type" in request is "PUSH"
    Given JSON Pointer "/socket_method" in request is "Bind"


    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I store "/zato_outgoing_zmq_edit_response/id" from response under "def_id"
    And JSON Pointer "/zato_outgoing_zmq_edit_response/id" is any integer
    And I sleep for "2"


  @outgoing.zmq.edit
  Scenario: Delete created ZMQ connection

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.outgoing.zmq.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#def_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
