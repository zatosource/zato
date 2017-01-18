@server
Feature: zato.server.get-by-id
    Updates server’s information in the ODB

    @server.edit
    Scenario: Set up

        Given I store a random string under "test_name1"

    @server.edit
    Scenario: Get information on a Zato test server1

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.server.get-by-id"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "@server1_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_server_get_by_id_response/id" is an integer "@server1_id"
        And JSON Pointer "/zato_server_get_by_id_response/cluster_id" is an integer "$ZATO_API_TEST_CLUSTER_ID"
        And JSON Pointer "/zato_server_get_by_id_response/name" is "@server1_name"
        And JSON Pointer "/zato_server_get_by_id_response/host" is "@server_host"

    @server.edit
    Scenario: Update server1's information

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.server.edit"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "@server1_id"
        Given JSON Pointer "/name" in request is "#test_name1"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_server_edit_response/id" is an integer "@server1_id"
        And JSON Pointer "/zato_server_edit_response/cluster_id" is an integer "$ZATO_API_TEST_CLUSTER_ID"
        And JSON Pointer "/zato_server_edit_response/name" is "#test_name1"
        And JSON Pointer "/zato_server_edit_response/host" is "@server_host"

    @server.edit
    Scenario: Check that correct information is returned for server1

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.server.get-by-id"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "@server1_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_server_get_by_id_response/id" is an integer "@server1_id"
        And JSON Pointer "/zato_server_get_by_id_response/cluster_id" is an integer "$ZATO_API_TEST_CLUSTER_ID"
        And JSON Pointer "/zato_server_get_by_id_response/name" is "#test_name1"
        And JSON Pointer "/zato_server_get_by_id_response/host" is "@server_host"

    @server.edit
    Scenario: Rename server1 back to its original name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.server.edit"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "@server1_id"
        Given JSON Pointer "/name" in request is "@server1_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_server_edit_response/id" is an integer "@server1_id"
        And JSON Pointer "/zato_server_edit_response/cluster_id" is an integer "$ZATO_API_TEST_CLUSTER_ID"
        And JSON Pointer "/zato_server_edit_response/name" is "@server1_name"
        And JSON Pointer "/zato_server_edit_response/host" is "@server_host"

    @server.edit
    Scenario: Check again that correct information is returned for server1

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.server.get-by-id"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "@server1_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_server_get_by_id_response/id" is an integer "@server1_id"
        And JSON Pointer "/zato_server_get_by_id_response/cluster_id" is an integer "$ZATO_API_TEST_CLUSTER_ID"
        And JSON Pointer "/zato_server_get_by_id_response/name" is "@server1_name"
        And JSON Pointer "/zato_server_get_by_id_response/host" is "@server_host"
