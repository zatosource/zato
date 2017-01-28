
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

    Then response is equal to "{"response":{"bool1":false, "bool2":true}}"

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
