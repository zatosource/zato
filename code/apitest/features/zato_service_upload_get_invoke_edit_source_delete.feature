Feature: zato.service upload-get-invoke-edit-source-delete
    @enabled
    Scenario: Set up

        Given I store a random string under "payload_name"
        Given I store a random string under "payload_request"
        Given I encode "#payload_request" using Base64 under "encoded_request"
        Given I store a format string "{payload_name}.py" under "payload_name_py"
        Given I store a format string "{payload_name}.apitest_service_operations" under "service_name"
        Given I store a random integer under "threshold"
        Given I decode "@apitest_service_operations_payload" using Base64 under "decoded_source"
        Given I encode "#decoded_source" using Base64 under "encoded_source"

    @enabled
    Scenario: Invoke zato.service.upload-package 

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.upload-package"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/payload" in request is "@apitest_service_operations_payload"
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
    Scenario: Invoke zato.service.edit to set is_active as False and random slow_threshold

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.edit"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#service_id"
        Given JSON Pointer "/is_active" in request is "false"
        Given JSON Pointer "/slow_threshold" in request is "#threshold"

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

        And I decode "#payload_response" using Base64 under "decoded_response"
        And variable "#decoded_response" is a string "#payload_request" 

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.get-source-info to check that the source is the same uploaded

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.get-source-info"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "#service_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_service_get_source_info_response/source" is "#encoded_source"

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