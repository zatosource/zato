Feature: zato.security.tech-account.*

    Scenario: Set up

        Given I store a random string under "url_path"
        Given I store a random string under "tech_name"
        Given I store a random string under "tech_username"
        Given I store a random string under "tech_password"

    Scenario: Invoke zato.security.tech-account.create

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.security.tech-account.create"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "#tech_username"
        Given JSON Pointer "/is_active" in request is "true"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_security_tech_account_create_response/name" from response under "tech_name"
        And I store "/zato_security_tech_account_create_response/id" from response under "tech_id"

        And I sleep for "1"

    Scenario: Invoke zato.security.tech-account.change-password

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.security.tech-account.change-password"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#tech_id"
        Given JSON Pointer "/password1" in request is "#tech_password"
        Given JSON Pointer "/password2" in request is "#tech_password"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    Scenario: Create HTTP channel for zato.ping service to be executed with the security definition created

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
        Given JSON Pointer "/url_path" in request is "/apitest/security/tech-account/ping"
        Given JSON Pointer "/service" in request is "zato.ping"
        Given JSON Pointer "/data_format" in request is "json"
        Given JSON Pointer "/method" in request is "GET"
        Given JSON Pointer "/security_id" in request is "#tech_id"

        When the URL is invoked

        Then status is "200"
        And I store "/zato_http_soap_create_response/name" from response under "ping_channel_name"
        And I store "/zato_http_soap_create_response/id" from response under "ping_channel_id"

        And I sleep for "1"

    Scenario: Invoke zato.ping over the previusly created http channel with valid credentials

        Given address "$ZATO_API_TEST_SERVER"
        Given header "X_ZATO_USER" "#tech_username"
        Given header "X_ZATO_PASSWORD" "#tech_password"

        Given URL path "/apitest/security/tech-account/ping"

        Given format "JSON"
        Given request is "{}"

        When the URL is invoked

        Then status is "200"

        Then JSON Pointer "/zato_ping_response/pong" is "zato"

        And I sleep for "1"

    Scenario: Invoke to fail zato.ping over the previusly created http channel with invalid credentials

        Given address "$ZATO_API_TEST_SERVER"
        Given header "X_ZATO_USER" "#tech_username"
        Given header "X_ZATO_PASSWORD" "failed password"

        Given URL path "/apitest/security/tech-account/ping"

        Given format "JSON"
        Given request is "{}"

        When the URL is invoked

        Then status is "401"
        And JSON Pointer "/zato_env/result" is "ZATO_ERROR"

        And I sleep for "1"

    Scenario: Invoke zato.security.tech-account.edit with random data and is_active false to test that it cannot be used

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.security.tech-account.edit"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#tech_id"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is a random string
        Given JSON Pointer "/is_active" in request is "false"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_security_tech_account_edit_response/name" from response under "tech_edit_name"

        And I sleep for "1"

    Scenario: Invoke zato.security.tech-account.get-by-id

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.security.tech-account.get-by-id"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#tech_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_security_tech_account_get_by_id_response/is_active" is False
        And JSON Pointer "/zato_security_tech_account_get_by_id_response/id" is "#tech_id"
        And JSON Pointer "/zato_security_tech_account_get_by_id_response/name" is "#tech_edit_name"

        And I sleep for "1"

    Scenario: Delete created HTTP channel for zato.ping

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.http-soap.delete"
        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#ping_channel_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"

    Scenario: Invoke zato.security.tech-account.delete

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.security.tech-account.delete"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#tech_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And I sleep for "1"
