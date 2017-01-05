@stats
Feature: zato.stats.summary.get-summary-by-week
    Return a list of summaries of statistics across all services for a given week.

    @stats.summary.get-summary-by-week
    Scenario: Set up

        Given I store UTC now under "utc_now" "default"
        Given I store "3" under "n_of_services"
        Given I store "usage" under "n_type"

    @stats.summary.get-summary-by-week
    Scenario: Get a list of summaries for a given week

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.stats.summary.get-summary-by-week"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is "#utc_now"
        Given JSON Pointer "/n" in request is an integer "#n_of_services"
        Given JSON Pointer "/n_type" in request is "#n_type"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_stats_get_summary_by_week_response" isn't empty
