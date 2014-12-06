Feature: scheduler.job.interval_based.type

    @enabled
    Scenario: Log in to Zato Public API and create a job

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.scheduler.job.create"

        Given format "JSON"
        Given request is "{}"

        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is a random string
        Given JSON Pointer "/is_active" in request is "true"
        Given JSON Pointer "/job_type" in request is "interval_based"
        Given JSON Pointer "/service" in request is "zato.stats.aggregate-by-day"
        Given JSON Pointer "/start_date" in request is UTC now "default"
        Given JSON Pointer "/weeks" in request is a random integer

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And JSON Pointer "/zato_scheduler_job_create_response/id" isn't empty
        And JSON Pointer "/zato_scheduler_job_create_response/name" isn't empty
        And JSON Pointer "/zato_scheduler_job_create_response/cron_definition" is empty

        And I store "/zato_scheduler_job_create_response/name" from response under "job_name"
        And I store "/zato_scheduler_job_create_response/id" from response under "job_id"

    @enabled
    Scenario: Get the job by name

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.scheduler.job.get-by-name"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is "#job_name"
        Given I store "request" under "request"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And JSON Pointer "/zato_scheduler_job_get_by_name_response/id" is "#job_id"
        And JSON Pointer "/zato_scheduler_job_get_by_name_response/name" is "#job_name"

    @enabled
    Scenario: Get list of jobs and check if the created job is part of it

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.scheduler.job.get-list"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And JSON Pointer "/zato_scheduler_job_get_list_response/0/id" is "#job_id"
        And JSON Pointer "/zato_scheduler_job_get_list_response/0/name" is "#job_name"

    @enabled
    Scenario: Edit the job

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.scheduler.job.edit"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is "#job_id"
        Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
        Given JSON Pointer "/name" in request is a random string
        Given JSON Pointer "/is_active" in request is "true"
        Given JSON Pointer "/job_type" in request is "interval_based"
        Given JSON Pointer "/service" in request is "zato.stats.aggregate-by-day"
        Given JSON Pointer "/start_date" in request is UTC now "default"
        Given JSON Pointer "/weeks" in request is a random integer

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

        And JSON Pointer "/zato_scheduler_job_edit_response/id" is "#job_id"

        And I store "/zato_scheduler_job_edit_response/id" from response under "edited_job_id"

    @enabled
    Scenario: Execute the edited job

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.scheduler.job.execute"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is an integer "#edited_job_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"

    @enabled
    Scenario: Delete the edited job

        Given address "$ZATO_API_TEST_SERVER"
        Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

        Given URL path "/zato/json/zato.scheduler.job.delete"

        Given format "JSON"
        Given request is "{}"
        Given JSON Pointer "/id" in request is an integer "#edited_job_id"

        When the URL is invoked

        Then status is "200"
        And JSON Pointer "/zato_env/result" is "ZATO_OK"
