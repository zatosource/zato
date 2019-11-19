@stats
Feature: zato.stats.summary.get-summary-by-month
    Return a list of summaries of statistics across all services for a given month.

    @stats.summary.get-summary-by-month
    Scenario: Set up

        Given I store UTC now under "utc_now" "default"
        Given I store "3" under "n_of_services"
        Given I store "usage" under "n_type"

    @stats.summary.get-summary-by-month
    Scenario: Get a list of summaries for a given month

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.stats.summary.get-summary-by-month"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is "#utc_now"
        Given JSON Pointer "/n" in request is an integer "#n_of_services"
        Given JSON Pointer "/n_type" in request is "#n_type"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_stats_get_summary_by_month_response" isn't empty
