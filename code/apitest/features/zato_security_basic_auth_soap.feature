@basic-auth.soap
Feature: zato.security.basic-auth.create
    Create a basic auth definition,
    and check that it works against a new
    ping endpoint
    clean up after is done

    @soap-security.basic-auth.create
    Scenario: Set up

        Given I store a random string under "url_path"
        Given I store a random string under "basic_username"
        Given I store a random string under "basic_password"

    @soap-security.basic-auth.create
    Scenario: Invoke zato.security.basic-auth.create

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"
        Given URL path "/zato/soap"
        Given SOAP action "zato:zato_security_basic_auth_create_request"
        Given HTTP method "POST"
        Given format "XML"

        Given XPath "//cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given XPath "//name" in request is a random string
        Given XPath "//is_active" in request is "true"
        Given XPath "//username" in request is "#basic_username"
        Given XPath "//realm" in request is a random string

        When the URL is invoked

        Then status is "200"
        And XPath "//zato_env//result" is "ZATO_OK"
        And I store "//zato_security_basic_auth_create_response//item//name" from response under "basic_name"
        And I store "//zato_security_basic_auth_create_response//item//id" from response under "basic_id"

        And I sleep for "1"