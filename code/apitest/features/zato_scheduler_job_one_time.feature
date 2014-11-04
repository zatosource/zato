Feature: Zato scheduler job, one_time type

Scenario: Log in to Zato Public API and upload custom set-key service

    Given address "@test_server"
    Given URL path "/zato/json/zato.service.upload-package"

    Given Basic Auth "@pubapi_user" "@pubapi_password"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "@cluster_id"
    Given JSON Pointer "/payload" in request is "@set_key_service_payload"
    Given JSON Pointer "/payload_name" in request is "set_key.py"

    Given I store a random string under "set_key_value"

    When the URL is invoked

    Then status is "200"
    And I sleep for "2"

Scenario: Upload custom get-key service

    Given address "@test_server"
    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "@cluster_id"
    Given JSON Pointer "/payload" in request is "@get_key_service_payload"
    Given JSON Pointer "/payload_name" in request is "get_key.py"

    When the URL is invoked

    Then status is "200"
    And I sleep for "2"

Scenario: Create a job for newly uploaded custom set-key service

    Given address "@test_server"
    Given URL path "/zato/json/zato.scheduler.job.create"

    Given format "JSON"
    Given request is "{}"

    Given JSON Pointer "/cluster_id" in request is "@cluster_id"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/job_type" in request is "one_time"
    Given JSON Pointer "/service" in request is "set-key.set-key"
    Given JSON Pointer "/start_date" in request is UTC now "default"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And JSON Pointer "/zato_scheduler_job_create_response/id" isn't empty
    And JSON Pointer "/zato_scheduler_job_create_response/name" isn't empty
    And JSON Pointer "/zato_scheduler_job_create_response/cron_definition" is empty

    And I store "/zato_scheduler_job_create_response/id" from response under "set_key_job_id"
    And I store "/zato_scheduler_job_create_response/name" from response under "set_key_job_name"

    And I sleep for "1"

Scenario: Get the set-key job by name

    Given address "@test_server"
    Given URL path "/zato/json/zato.scheduler.job.get-by-name"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "@cluster_id"
    Given JSON Pointer "/name" in request is "#set_key_job_name"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And JSON Pointer "/zato_scheduler_job_get_by_name_response/id" is "#set_key_job_id"
    And JSON Pointer "/zato_scheduler_job_get_by_name_response/name" is "#set_key_job_name"

Scenario: Edit the set-key job

    Given address "@test_server"
    Given URL path "/zato/json/zato.scheduler.job.edit"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#set_key_job_id"
    Given JSON Pointer "/cluster_id" in request is "@cluster_id"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/job_type" in request is "one_time"
    Given JSON Pointer "/service" in request is "set-key.set-key"
    Given JSON Pointer "/start_date" in request is a random date after "2014-09-30" "default"
    Given JSON Pointer "/extra" in request is "#set_key_value"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And JSON Pointer "/zato_scheduler_job_edit_response/id" is "#set_key_job_id"

    And I store "/zato_scheduler_job_edit_response/id" from response under "edited_job_id"

    And I sleep for "1"

Scenario: Execute the edited set-key job

    Given address "@test_server"
    Given URL path "/zato/json/zato.scheduler.job.execute"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is an integer "#edited_job_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

    And I sleep for "1"

Scenario: Delete the edited set-key job

    Given address "@test_server"
    Given URL path "/zato/json/zato.scheduler.job.delete"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is an integer "#edited_job_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

Scenario: Create HTTP channel for get-key service to be executed through

    Given address "@test_server"
    Given URL path "/zato/json/zato.http-soap.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "@cluster_id"
    Given JSON Pointer "/name" in request is a random string
    Given JSON Pointer "/is_active" in request is "true"
    Given JSON Pointer "/connection" in request is "channel"
    Given JSON Pointer "/transport" in request is "plain_http"
    Given JSON Pointer "/is_internal" in request is "false"
    Given JSON Pointer "/url_path" in request is "/my-service/get-key.get-key"
    Given JSON Pointer "/service" in request is "get-key.get-key"
    Given JSON Pointer "/data_format" in request is "json"
    Given JSON Pointer "/method" in request is "GET"

    When the URL is invoked

    Then status is "200"
    And I store "/zato_http_soap_create_response/name" from response under "channel_name"

    And I sleep for "1"

Scenario: Execute get-key service through HTTP channel

    Given address "@test_server"
    Given URL path "/my-service/get-key.get-key"
    Given format "JSON"

    When the URL is invoked

    Then JSON Pointer "/response/value" is "#set_key_value"
