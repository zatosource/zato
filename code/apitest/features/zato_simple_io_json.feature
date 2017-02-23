
# ################################################################################################################################

@simple-io
Feature: simple-io.json
  SimpleIO tests for JSON data format

# ################################################################################################################################

  Scenario: AsIs datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.as-is-service"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "id1"
    Given JSON Pointer "/a_id" in request is "a1"
    Given JSON Pointer "/b_count" in request is "b1"
    Given JSON Pointer "/c_size" in request is "c1"
    Given JSON Pointer "/d_timeout" in request is "d1"
    Given JSON Pointer "/is_e" in request is "e1"
    Given JSON Pointer "/needs_f" in request is "f1"
    Given JSON Pointer "/should_g" in request is "g1"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/id" is "id2"
    And JSON Pointer "/response/a_id" is "a2"
    And JSON Pointer "/response/b_count" is "b2"
    And JSON Pointer "/response/c_size" is "c2"
    And JSON Pointer "/response/d_timeout" is "d2"
    And JSON Pointer "/response/is_e" is "e2"
    And JSON Pointer "/response/needs_f" is "f2"
    And JSON Pointer "/response/should_g" is "g2"

# ################################################################################################################################

  Scenario: Boolean datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.boolean-service"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/bool1" in request is "True"
    Given JSON Pointer "/bool2" in request is "False"

    When the URL is invoked
    Then status is "200"

    Then JSON response is equal to "{"response":{"bool1":false, "bool2":true}}"

# ################################################################################################################################

  Scenario: CSV datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.csv-service"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/csv1" in request is "1,11,111,1111"
    Given JSON Pointer "/csv2" in request is "2,22,222,2222"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/csv3" is "3,33,333,3333"
    And JSON Pointer "/response/csv4" is "4,44,444,4444"

# ################################################################################################################################

  Scenario: Dict datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.dict-service"

    Given format "JSON"
    Given request is "{"dict1":{}, "dict2":{}}"
    Given JSON Pointer "/dict1/key1_1" in request is "value1_1"
    Given JSON Pointer "/dict1/key1_2" in request is "value1_2"
    Given JSON Pointer "/dict2/key2_1" in request is "value2_1"
    Given JSON Pointer "/dict2/key2_2" in request is "value2_2"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/dict3/key3_1" is "value3_1"
    And JSON Pointer "/response/dict3/key3_2" is "value3_2"
    And JSON Pointer "/response/dict4/key4_1" is "value4_1"
    And JSON Pointer "/response/dict4/key4_2" is "value4_2"

# ################################################################################################################################

  Scenario: Integer datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.integer-service"

    Given format "JSON"
    Given request is "{"int1":1, "int2":2}"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/int3" is an integer "3"
    And JSON Pointer "/response/int4" is an integer "4"

# ################################################################################################################################

  Scenario: List datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.list-service"

    Given format "JSON"
    Given request is "{"list1":["1", "2", "3"], "list2":["4", "5", "6"]}"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/list3" is a list ""7","8","9""
    And JSON Pointer "/response/list4" is a list ""10","11","12""

# ################################################################################################################################

  Scenario: ListOfDicts datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.list-of-dicts-service"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/lod1" in request is "[{"k111":"v111", "k112":"v112"}, {"k121":"v121", "k122":"v122"}]" (with literal_eval)
    Given JSON Pointer "/lod2" in request is "[{"k211":"v211", "k212":"v212"}, {"k221":"v221", "k222":"v222"}]" (with literal_eval)

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/lod3" is "[{"k311":"v311", "k312":"v312"}, {"k321":"v321", "k322":"v322"}]" (with literal_eval)
    And JSON Pointer "/response/lod4" is "[{"k411":"v411", "k412":"v412"}, {"k421":"v421", "k422":"v422"}]" (with literal_eval)

# ################################################################################################################################

  Scenario: Prefixes and suffixes
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.no-force-type-service"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/aa1" in request is "aa1-value"
    Given JSON Pointer "/bb1" in request is "bb1-value"
    Given JSON Pointer "/a_id" in request is "1"
    Given JSON Pointer "/a_count" in request is "2"
    Given JSON Pointer "/a_size" in request is "3"
    Given JSON Pointer "/a_timeout" in request is "4"
    Given JSON Pointer "/is_b" in request is "true"
    Given JSON Pointer "/needs_b" in request is "false"
    Given JSON Pointer "/should_b" in request is "true"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/aa2" is an integer "11"
    And JSON Pointer "/response/bb2" is an integer "22"
    And JSON Pointer "/response/c_id" is an integer "33"
    And JSON Pointer "/response/c_count" is an integer "44"
    And JSON Pointer "/response/c_size" is an integer "55"
    And JSON Pointer "/response/c_timeout" is an integer "66"
    And JSON Pointer "/response/is_d" is False
    And JSON Pointer "/response/needs_d" is True
    And JSON Pointer "/response/should_d" is False

# ################################################################################################################################

  Scenario: Unicode datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.unicode-service"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/uni_a" in request is "a"
    Given JSON Pointer "/uni_b" in request is "b"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/uni_c" is "c"
    And JSON Pointer "/response/uni_d" is "d"

# ################################################################################################################################

  Scenario: UTC datatype
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/json/zato.checks.sio.utc-service"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/utc1" in request is "2019-01-26T22:33:44+00:00"
    Given JSON Pointer "/utc2" in request is "2023-12-19T21:31:41+00:00"

    When the URL is invoked
    Then status is "200"

    And JSON Pointer "/response/utc1" is "1234-11-22T01:02:03"
    And JSON Pointer "/response/utc2" is "2918-03-19T21:22:23"

# ################################################################################################################################
