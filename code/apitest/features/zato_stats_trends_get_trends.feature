@stats
Feature: zato.stats.get-trends
    Return top N slowest or most commonly used services for a given period along with their trends.

    @stats.get-trends
    Scenario: Set up

        Given I store "2017-01-04T16:09:00" under "start"
        Given I store "2017-01-04T19:09:00" under "stop"
        Given I store "3" under "n_of_slowest"
        Given I store "usage" under "n_type"

    @stats.get-trends
    Scenario: Get trends of n slowest of most commonly used services

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.stats.trends.get-trends"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is "#start"
        Given JSON Pointer "/stop" in request is "#stop"
        Given JSON Pointer "/n" in request is an integer "#n_of_slowest"
        Given JSON Pointer "/n_type" in request is "#n_type"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_stats_get_trends_response" isn't empty
