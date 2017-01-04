@stats
Feature: zato.stats.get-by-service
    Return statistics of a service for a given period along with a trends data broken down by each minute in that interval

    @stats.get-by-service
    Scenario: Set up

        Given I store "325" under "service_id"
        Given I store "zato.outgoing.sql.auto-ping" under "service_name"
        Given I store UTC now under "utc_now" "default"

    @stats.get-by-service
    Scenario: Get statistics of a service

	Given address "$ZATO_API_TEST_SERVER"
	Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

	Given URL path "/zato/json/zato.stats.get-by-service"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/start" in request is "2017-01-04T14:45:00"
        Given JSON Pointer "/stop" in request is "2017-01-04T16:45:00"
        #Given JSON Pointer "/start" in request is a random date before "#utc_now" "default"
        #Given JSON Pointer "/stop" in request is a random date after "#utc_now" "default"
        Given JSON Pointer "/service_id" in request is "#service_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
        And JSON Pointer "/zato_stats_get_by_service_response/service_name" is "#service_name"
        And JSON Pointer "/zato_stats_get_by_service_response/usage" isn't empty
        And JSON Pointer "/zato_stats_get_by_service_response/rate" isn't empty
        And JSON Pointer "/zato_stats_get_by_service_response/time" isn't empty
        And JSON Pointer "/zato_stats_get_by_service_response/usage_trend" isn't empty
        And JSON Pointer "/zato_stats_get_by_service_response/mean_trend" isn't empty
        And JSON Pointer "/zato_stats_get_by_service_response/min_resp_time" isn't empty
        And JSON Pointer "/zato_stats_get_by_service_response/max_resp_time" isn't empty
