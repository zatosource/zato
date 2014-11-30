Feature: zato.ping2

    Scenario: Invoke zato.ping2 to check if zato is up

        Given address "$ZATO_API_TEST_SERVER"

        Given URL path "/zato/ping2"

        Given format "JSON"
        Given request is "{}"
        
        When the URL is invoked

        Then JSON Pointer "/zato_ping2_response/pong" is "zato"
        
