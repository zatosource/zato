Feature: zato.kvdb.remote-command

    @enabled
    Scenario: Set up

        Given I store a random string under "list_key"
        Given I store a random string under "hash_key"
        Given I store a random string under "string_key"

        Given I store a random string under "value_a"
        Given I store a random string under "value_b"
        Given I store a random string under "value_c"

        Given I store a format string "['{value_c}', '{value_b}', '{value_a}']" under "list_result"

        Given I store a format string "LPUSH apitest:list:{list_key} {value_a} {value_b} {value_c}" under "command_create_list"
        Given I store a format string "LRANGE apitest:list:{list_key} 0 -1" under "command_get_list"
        Given I store a format string "DEL apitest:list:{list_key}" under "command_delete_list"
        Given I store a format string "EXISTS apitest:list:{list_key}" under "command_exists_list"

        Given I store a format string "HSETNX apitest:hash:{hash_key} {value_a} {value_b}" under "command_create_hash"
        Given I store a format string "HGET apitest:hash:{hash_key} {value_a}" under "command_get_hash"
        Given I store a format string "DEL apitest:hash:{hash_key}" under "command_delete_hash"
        Given I store a format string "EXISTS apitest:hash:{hash_key}" under "command_exists_hash"

        Given I store a format string "SET apitest:string:{string_key} {value_b}" under "command_create_string"
        Given I store a format string "GET apitest:string:{string_key}" under "command_get_string"
        Given I store a format string "DEL apitest:string:{string_key}" under "command_delete_string"
        Given I store a format string "EXISTS apitest:string:{string_key}" under "command_exists_string"

    @enabled
    Scenario: Create a test list entry in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_create_list"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        Then JSON Pointer "/zato_kvdb_remote_command_execute_response/result" is an integer "3"

        And I sleep for "1"

    @enabled
    Scenario: Read the test list in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_get_list"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        Then JSON Pointer "/zato_kvdb_remote_command_execute_response/result" is "#list_result"

        And I sleep for "1"

    @enabled
    Scenario: Delete the test list entry in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_delete_list"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    @enabled
    Scenario: Check that the test list doesn't exists in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_exists_list"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        Then JSON Pointer "/zato_kvdb_remote_command_execute_response/result" is "(None)"

        And I sleep for "1"

    @enabled
    Scenario: Create a test hashmap entry for command_hash_a in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_create_hash"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    @enabled
    Scenario: Read the test hash_map in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_get_hash"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        Then JSON Pointer "/zato_kvdb_remote_command_execute_response/result" is "#value_b"

        And I sleep for "1"

    @enabled
    Scenario: Delete the test hash_map entry in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_delete_hash"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    @enabled
    Scenario: Check that the test hash_map doesn't exists in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_exists_hash"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        Then JSON Pointer "/zato_kvdb_remote_command_execute_response/result" is "(None)"

        And I sleep for "1"

	@enabled
    Scenario: Create a test string entry in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_create_string"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    @enabled
    Scenario: Read a test string entry in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_get_string"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        Then JSON Pointer "/zato_kvdb_remote_command_execute_response/result" is "#value_b"

        And I sleep for "1"

    @enabled
    Scenario: Delete a test string entry in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_delete_string"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    @enabled
    Scenario: Check that the test string entry doesn't exists in a cluster's KVDB

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.kvdb.remote-command.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/command" in request is "#command_exists_string"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        Then JSON Pointer "/zato_kvdb_remote_command_execute_response/result" is "(None)"

        And I sleep for "1"
