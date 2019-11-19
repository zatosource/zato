@http-soap
Feature: zato.http-soap.delete
  Deletes a plain HTTP or SOAP object, this can be either channel or an outgoing connection.

  @http-soap.delete
  Scenario: Set up
    Given I store "apitest.outconn" under "outconn_name"

### Test Delete HTTP Connections  ###

  @http-soap.delete
  Scenario: Create JSON HTTP channel for zato.ping

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.http-soap.create"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is a random string
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/connection" in request is "channel"
      Given JSON Pointer "/transport" in request is "plain_http"
      Given JSON Pointer "/is_internal" in request is "false"
      Given JSON Pointer "/url_path" in request is "/apitest/httpcreate/test"
      Given JSON Pointer "/service" in request is "zato.ping"
      Given JSON Pointer "/data_format" in request is "json"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "service_channel_name"
      And I store "/zato_http_soap_create_response/id" from response under "service_channel_id"
      And I sleep for "1"


  @http-soap.delete
  Scenario: Invoke zato.ping through created http channel using JSON

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/httpcreate/test"

    Given format "JSON"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON pointer "/zato_ping_response/pong" is "zato"


  @http-soap.delete
  Scenario: Delete created HTTP channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#service_channel_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


### Test Outgoing Connections ###

  @http-soap.delete
  Scenario: Upload test_service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request "service_upload.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And I sleep for "1"


  @http-soap.delete
  Scenario: Create an outgoing HTTP connection which points to the test HTTP channel we created

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.http-soap.create"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is "#outconn_name"
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/connection" in request is "outgoing"
      Given JSON Pointer "/transport" in request is "plain_http"
      Given JSON Pointer "/is_internal" in request is "false"
      Given JSON Pointer "/url_path" in request is "/apitest/test-service"
      Given JSON Pointer "/host" in request is "$ZATO_API_TEST_SERVER"
      Given JSON Pointer "/data_format" in request is "json"
      Given JSON Pointer "/ping_method" in request is "HEAD"
      Given JSON Pointer "/pool_size" in request is "20"
      Given JSON Pointer "/timeout" in request is "10"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "outconn_name"
      And I store "/zato_http_soap_create_response/id" from response under "outconn_id"
      And I sleep for "1"


  ### Outgoing connection ApiTest clean up ###
  @http-soap.delete
  Scenario: Delete Outgoing connection

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#outconn_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


  #### Remove services ####

  @http-soap.delete
  Scenario: Get test_service details by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-by-name"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "test-service.test-service"
    When the URL is invoked

    Then status is "200"

    And I store "/zato_service_get_by_name_response/id" from response under "test_service_id"

  @http-soap.delete
  Scenario: Delete test service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#test_service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

### End test outgoing connections ###