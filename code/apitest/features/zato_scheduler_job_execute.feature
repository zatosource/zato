@scheduler
Feature: zato.scheduler.job.execute
  Executes a scheduler’s job by ID. The job’s invocation doesn’t count towards its scheduled execution plan, e.g. 
  it won’t make it skip the next time it’s scheduled to run.
  
  @scheduler.job.execute
  Scenario: Create a new interval based job scheduler

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

    And I store "/zato_scheduler_job_create_response/id" from response under "interval_job_id"
    And I store "/zato_scheduler_job_create_response/name" from response under "interval_job_name"


  @scheduler.job.execute
  Scenario: Create a new one time job scheduler

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.scheduler.job.create"

    Given format "JSON"
    Given request is "{}"

    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/job_type" in request is "one_time"
    Given JSON Pointer "/service" in request is "zato.ping"
    Given JSON Pointer "/start_date" in request is UTC now "default"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And JSON Pointer "/zato_scheduler_job_create_response/id" isn't empty
    And JSON Pointer "/zato_scheduler_job_create_response/name" isn't empty
    And JSON Pointer "/zato_scheduler_job_create_response/cron_definition" is empty

    And I store "/zato_scheduler_job_create_response/id" from response under "one_time_job_id"
    And I store "/zato_scheduler_job_create_response/name" from response under "one_time_job_name"


  @scheduler.job.execute
  Scenario: Execute the scheduled interval job

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.scheduler.job.execute"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is an integer "#interval_job_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @scheduler.job.execute
  Scenario: Execute the one time scheduled job

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.scheduler.job.execute"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is an integer "#one_time_job_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @scheduler.job.execute
  Scenario: Delete the scheduled interval job

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.scheduler.job.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is an integer "#interval_job_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @scheduler.job.execute
  Scenario: Delete the one time scheduled job

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.scheduler.job.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is an integer "#one_time_job_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
