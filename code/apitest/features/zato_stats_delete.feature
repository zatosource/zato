@stats
Feature: zato.stats.delete
    Delete statistics for all services from a given period.

    @stats.delete
    Scenario: Set up

        Given I store "2017-01-04T18:30:00" under "start"
        Given I store "2017-01-04T18:45:00" under "stop"
        Given I store "3" under "n_of_services"
        Given I store "usage" under "n_type"

    @stats.delete
    Scenario: Get a list of summaries for a given interval 

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.stats.summary.get-summary-by-range"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is "#start"
        Given JSON Pointer "/stop" in request is "#stop"
        Given JSON Pointer "/n" in request is an integer "#n_of_services"
        Given JSON Pointer "/n_type" in request is "#n_type"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_stats_get_summary_by_range_response" isn't empty

    @stats.delete
    Scenario: Delete statistics from a given period

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.stats.delete"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is "#start"
        Given JSON Pointer "/stop" in request is "#stop"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

    @stats.delete
    Scenario: Check if the statistics has been actually deleted

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.stats.summary.get-summary-by-range"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is "#start"
        Given JSON Pointer "/stop" in request is "#stop"
        Given JSON Pointer "/n" in request is an integer "#n_of_services"
        Given JSON Pointer "/n_type" in request is "#n_type"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_stats_get_summary_by_range_response" isn't empty
