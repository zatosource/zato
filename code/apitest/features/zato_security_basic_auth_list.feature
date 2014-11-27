Feature: zato.security.basic-auth.get-list

    Scenario: Set up

        Given I store a random string under "url_path"
        
    Scenario: Create HTTP channel for zato.security.basic-auth.get-list service to be executed through

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.http-soap.create"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is a random string
        Given JSON Pointer "/is_active" in request is "true"
        Given JSON Pointer "/connection" in request is "channel"
        Given JSON Pointer "/transport" in request is "plain_http"
        Given JSON Pointer "/is_internal" in request is "false"
        Given JSON Pointer "/url_path" in request is "/apitest/security/basic-auth/list"
        Given JSON Pointer "/service" in request is "zato.security.basic-auth.get-list"
        Given JSON Pointer "/data_format" in request is "json"
        Given JSON Pointer "/method" in request is "GET"
        Given JSON Pointer "/security_id" in request is "ZATO_NONE"

        When the URL is invoked

        Then status is "200"
        And I store "/zato_http_soap_create_response/name" from response under "list_channel_list_name"
        And I store "/zato_http_soap_create_response/id" from response under "list_channel_list_id"

        And I sleep for "1"

    Scenario: Create HTTP channel for zato.security.basic-auth.delete service to be executed through

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.http-soap.create"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is a random string
        Given JSON Pointer "/is_active" in request is "true"
        Given JSON Pointer "/connection" in request is "channel"
        Given JSON Pointer "/transport" in request is "plain_http"
        Given JSON Pointer "/is_internal" in request is "false"
        Given JSON Pointer "/url_path" in request is "/apitest/security/basic-auth/delete"
        Given JSON Pointer "/service" in request is "zato.security.basic-auth.delete"
        Given JSON Pointer "/data_format" in request is "json"
        Given JSON Pointer "/method" in request is "GET"
        Given JSON Pointer "/security_id" in request is "ZATO_NONE"

        When the URL is invoked

        Then status is "200"
        And I store "/zato_http_soap_create_response/name" from response under "list_channel_delete_name"
        And I store "/zato_http_soap_create_response/id" from response under "list_channel_delete_id"

        And I sleep for "1"

    Scenario: Invoke zato.security.basic-auth.get-list over the previusly created http channel

        Given address "$ZATO_API_TEST_SERVER"

        Given URL path "/apitest/security/basic-auth/list"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        
        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_security_basic_auth_get_list_response" from response under "response_list"
        
        And I sleep for "1"

    Scenario: Delete created HTTP channel for zato.security.basic-auth.delete

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.http-soap.delete"
        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#list_channel_delete_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        
        And I sleep for "1"

    Scenario: Delete created HTTP channel for zato.security.basic-auth.get-list

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.http-soap.delete"
        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#list_channel_list_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        
        And I sleep for "1"
