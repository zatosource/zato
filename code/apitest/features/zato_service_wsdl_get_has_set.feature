Feature: zato.service wsdl_get_has_set
    @enabled
    Scenario: Set up

        Given I store a random string under "payload_name"
        Given I store a format string "{payload_name}.py" under "payload_name_py"
        Given I store a format string "{payload_name}.apitest_service_operations" under "service_name"
        Given I store a format string "{payload_name}.wsdl" under "wsdl_name"
        Given I decode "@apitest_service_operations_wsdl" using Base64 under "decoded_wsdl"
        Given I encode "#decoded_wsdl" using Base64 under "encoded_wsdl"

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
    Scenario: Invoke zato.service.has-wsdl to check that has_wsdl is False

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.has-wsdl"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "#service_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_service_has_wsdl_response/has_wsdl" is False

        And I store "/zato_service_has_wsdl_response/service_id" from response under "service_id"

        And I sleep for "1"


    @enabled
    Scenario: Invoke zato.service.set-wsdl

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.set-wsdl"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "#service_name"
        Given JSON Pointer "/wsdl" in request is "@apitest_service_operations_wsdl"
        Given JSON Pointer "/wsdl_name" in request is "#wsdl_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.get-wsdl

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.get-wsdl"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/service" in request is "#service_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_service_get_wsdl_response/wsdl_name" is "#wsdl_name"
        And JSON Pointer "/zato_service_get_wsdl_response/wsdl" is "#encoded_wsdl"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.has-wsdl to check that has_wsdl is true

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.has-wsdl"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "#service_name"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_service_has_wsdl_response/has_wsdl" is True

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