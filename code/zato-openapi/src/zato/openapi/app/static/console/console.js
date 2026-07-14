(function() {

    // Configuration for the API reference widget
    var config = {
        url: '/openapi/console/openapi.json',
        hideClientButton: true,
        agent: {disabled: true},
        mcp: {disabled: true},
    };

    // Render the reference into its container
    window.Scalar.createApiReference('#console-reference', config);

})();
