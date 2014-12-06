Feature: zato.ping

    @enabled
    Scenario: Invoke ping to check if zato is up

        Given address "$ZATO_API_TEST_SERVER"

        Given URL path "/zato/ping"

        Given format "JSON"
        Given request is "{}"

        When the URL is invoked

        Then JSON Pointer "/zato_ping_response/pong" is "zato"

