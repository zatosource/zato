@stats
Feature: zato.stats.get-by-service
    Return statistics of a service for a given period along with a trends data broken down by each minute in that interval

    @stats.get-by-service
    Scenario: Set up

        Given I store "8" under "service_id"

    @stats.get-by-service
    Scenario: Get statistics of a service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.stats.get-by-service"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is UTC now "default" minus one hour
        Given JSON Pointer "/stop" in request is UTC now "default"
        Given JSON Pointer "/service_id" in request is "#service_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_stats_get_by_service_response" isn't an empty list
