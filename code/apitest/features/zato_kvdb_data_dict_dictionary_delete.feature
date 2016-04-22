@kvdb.data-dict
Feature: kvdb.data.dict.dictionary.delete
  Deletes a data dictionary entry from a cluster’s KVDB by the entry’s ID along with any translations the entry may constitue a part of.


  @kvdb.data-dict.delete
  Scenario: Set up

    Given I store a random string under "test_system"
    Given I store a random string under "test_key"
    Given I store a random string under "test_value"

  @kvdb.data-dict.delete
  Scenario: Create data dictionary test entry in a cluster's KVDB

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/system" in request is "#test_system"
    Given JSON Pointer "/key" in request is "#test_key"
    Given JSON Pointer "/value" in request is "#test_value"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And I store "/zato_kvdb_data_dict_dictionary_create_response/id" from response under "last_dictionary_entry_id"

  @kvdb.data-dict.delete
  Scenario: Invoke get-last-id to check if test dictionary entry actually exists

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.get-last-id"
    Given format "JSON"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_kvdb_data_dict_dictionary_get_last_id_response/value" is an integer "#last_dictionary_entry_id"

  @kvdb.data-dict.delete
  Scenario: Delete test dictionary entry

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.dictionary.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#last_dictionary_entry_id"

    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_kvdb_data_dict_dictionary_delete_response/id" is an integer "#last_dictionary_entry_id"
