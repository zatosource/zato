@outgoing
Feature: zato.outgoing.zmq.create
  Allows one to create a ZeroMQ outgoing connection.


  @outgoing.zmq.create
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


  @outgoing.zmq.create
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
