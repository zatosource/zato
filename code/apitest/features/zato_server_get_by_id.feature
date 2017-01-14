@server
Feature: zato.server.get-by-id
    Return information regarding a Zato server by its ID

    @server.get-by-id
        Scenario: Set up

        Given I store "87965187515" under "nonexistent_id"

    @server.get-by-id
    Scenario: Get information on a Zato test server1

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.server.get-by-id"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "@server1_id"

        When the URL is invoked

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_server_get_by_id_response/id" is an integer "@server1_id"
        And JSON Pointer "/zato_server_get_by_id_response/cluster_id" is an integer "$ZATO_API_TEST_CLUSTER_ID"
        And JSON Pointer "/zato_server_get_by_id_response/name" is "@server1_name"
        And JSON Pointer "/zato_server_get_by_id_response/host" is "@server_host"

    @server.get-by-id
    Scenario: Get information on a Zato test server2

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.server.get-by-id"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "@server2_id"

        When the URL is invoked

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_server_get_by_id_response/id" is an integer "@server2_id"
        And JSON Pointer "/zato_server_get_by_id_response/cluster_id" is an integer "$ZATO_API_TEST_CLUSTER_ID"
        And JSON Pointer "/zato_server_get_by_id_response/name" is "@server2_name"
        And JSON Pointer "/zato_server_get_by_id_response/host" is "@server_host"

    @server.get-by-id
    Scenario: Check that no information is returned for a non-existent server

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.server.get-by-id"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#nonexistent_id"

        When the URL is invoked

        Then status is "500"
        And JSON Pointer "/zato_env/result" is "ZATO_ERROR"
