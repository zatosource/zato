@channel.zmq
Feature: zato.channel.zmq.delete
  Deletes a ZeroMQ channel. The channel’s underlying socket will be first stopped.


  @channel.zmq.delete
  Scenario: Create a new zmq channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.channel.zmq.create"

    Given format "JSON"
    Given request is "{}"

    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/address" in request is "127.0.0.1:33445"
    Given JSON Pointer "/socket_type" in request is "PULL"
    Given JSON Pointer "/socket_method" in request is "Bind"
    Given JSON Pointer "/pool_strategy" in request is "Single"
    Given JSON Pointer "/service_source" in request is "Zato"
    Given JSON Pointer "/service" in request is "zato.ping"
    Given JSON Pointer "/data_format" in request is "json"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_channel_zmq_create_response/id" from response under "channel_id"
    And I sleep for "2"


  @channel.zmq.delete
  Scenario: Delete zmq channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.channel.zmq.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#channel_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


