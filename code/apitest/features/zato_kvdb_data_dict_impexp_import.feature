@kvdb
Feature: kvdb.data.dict.dictionary.create
  Imports KVDB data previously exported using the web admin.

  @kvdb.data-dict.impexp.import
  Scenario: Import KVDB dict data

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.kvdb.data-dict.impexp.import"

    Given format "JSON"
    Given request "kvdb_data_dict_impexp_import.json"


    When the URL is invoked

    Then JSON Pointer "/zato_env/result" is "ZATO_OK"
