@http-soap
Feature: zato.http-soap.ping
  Pings an outgoing plain HTTP or SOAP connection by its ID.

  @http-soap.ping
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

  @http-soap.ping
  Scenario: Create an HTTP endpoint for test service that will be called using an outgoing connection

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
    Given JSON Pointer "/url_path" in request is "/apitest/test-service"
    Given JSON Pointer "/service" in request is "test-service.test-service"
    Given JSON Pointer "/data_format" in request is "json"


    When the URL is invoked

    Then status is "200"
    And I store "/zato_http_soap_create_response/name" from response under "test_service_name"
    And I store "/zato_http_soap_create_response/id" from response under "test_service_id"
    And I sleep for "1"

  @http-soap.ping
  Scenario: Upload outgoing_connection test service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request "service_outconn_test.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And I sleep for "1"


  @http-soap.ping
  Scenario: Create an outgoing HTTP connection which points to the test HTTP channel we created

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.create"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "apitest.outconn"
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


  @http-soap.ping
  Scenario: Ping outgoing_service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.ping"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#outconn_id"


    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_http_soap_ping_response/info" isn't empty


  @http-soap.ping
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


  @http-soap.ping
  Scenario: Delete Test Service HTTP Channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#test_service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @http-soap.ping
  Scenario: Get outgoing service details by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-by-name"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "outcon-test-service.out-conn-test-service"
    When the URL is invoked

    Then status is "200"

    And I store "/zato_service_get_by_name_response/id" from response under "outconn_service_id"

  @http-soap.ping
  Scenario: Delete Outgoing Test service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#outconn_service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @http-soap.ping
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

  @http-soap.ping
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
    