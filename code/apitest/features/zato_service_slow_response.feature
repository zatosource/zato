Feature: zato.service slow_response
    @enabled
    Scenario: Set up

        Given I store a random string under "payload_name"
        Given I store a random string under "payload_request"
        Given I encode "#payload_request" using Base64 under "encoded_request"
        Given I store a format string "{payload_name}.py" under "payload_name_py"
        Given I store a format string "{payload_name}.apitest_service_operations" under "service_name"

    @enabled
    Scenario: Invoke zato.service.upload-package 

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.upload-package"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/payload" in request is "@apitest_service_operations_sleep_payload"
        Given JSON Pointer "/payload_name" in request is "#payload_name_py"

        When the URL is invoked

        Then status is "200"
        And I sleep for "5"

    @enabled
    Scenario: Invoke zato.service.get-by-name to get service id

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.get-by-name"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "#service_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_service_get_by_name_response/id" from response under "service_id"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.edit to set slow_threshold to 3

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.edit"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#service_id"
        Given JSON Pointer "/is_active" in request is "true"
        Given JSON Pointer "/slow_threshold" in request is "3"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_service_edit_response/name" is "#service_name"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.invoke to check return response

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.invoke"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#service_id"
        Given JSON Pointer "/payload" in request is "#encoded_request"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_service_invoke_response/response" from response under "payload_response"
        And I store "/zato_env/cid" from response under "request_cid"

        And I decode "#payload_response" using Base64 under "decoded_response"
        And variable "#decoded_response" is a string "#payload_request"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.slow-response.get

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.slow-response.get"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cid" in request is "#request_cid"
        Given JSON Pointer "/name" in request is "#service_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_service_slow_response_get_response/req" is "#payload_request"
        And JSON Pointer "/zato_service_slow_response_get_response/resp" is "#payload_request"

        And I store "/zato_service_slow_response_get_response/req_ts" from response under "req_ts"
        And I store "/zato_service_slow_response_get_response/resp_ts" from response under "resp_ts"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.slow-response.get-list

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.slow-response.get-list"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/name" in request is "#service_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_service_slow_response_get_list_response/0/req_ts" is "#req_ts"
        And JSON Pointer "/zato_service_slow_response_get_list_response/0/resp_ts" is "#resp_ts"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.delete to remove the uploaded service

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.delete"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#service_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"