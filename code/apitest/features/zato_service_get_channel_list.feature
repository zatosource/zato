Feature: zato.service.get-channel-list

    @enabled
    Scenario: Invoke zato.service.get-by-name to get service id

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.get-by-name"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "zato.ping"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_service_get_by_name_response/id" from response under "service_id"

        And I sleep for "1"

    @enabled
    Scenario: Invoke zato.service.get-channel-list

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.service.get-channel-list"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#service_id"
        Given JSON Pointer "/channel_type" in request is "plain_http"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And I store "/zato_service_get_channel_list_response" from response under "list_response"

        And I sleep for "1"