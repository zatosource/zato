Feature: kvdb.data.dict.dictionary.delete

    Scenario: Set up

        Given I store a random string under "test_system"
        Given I store a random string under "test_key"
        Given I store a random string under "test_value"

    Scenario: Create data dictionary test entry in a cluster's KVDB

        Given address "@test_server"
        Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.create"
        Given Basic Auth "@pubapi_user" "@pubapi_password"
        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/system" in request is "#test_system"
        Given JSON Pointer "/key" in request is "#test_key"
        Given JSON Pointer "/value" in request is "#test_value"

        When the URL is invoked

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_kvdb_data_dict_dictionary_create_response/id" from response under "last_dictionary_entry_id"

    Scenario: Invoke get-last-id to check if test dictionary entry actually exists

        Given address "@test_server"
        Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.get-last-id"
        Given format "JSON"

        When the URL is invoked

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_kvdb_data_dict_dictionary_get_last_id_response/value" is an integer "#last_dictionary_entry_id"

    Scenario: Delete test dictionary entry

        Given address "@test_server"
        Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.delete"
        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#last_dictionary_entry_id"

        When the URL is invoked

        Then JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_kvdb_data_dict_dictionary_delete_response/id" is an integer "#last_dictionary_entry_id"
