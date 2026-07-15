(function() {

    // Configuration for the API reference widget - the document can be downloaded
    // in both JSON and YAML forms directly from the reference header.
    var config = {
        url: '/openapi/console/openapi.json',
        documentDownloadType: 'both',
        hideClientButton: true,
        agent: {disabled: true},
        mcp: {disabled: true},
    };

    // Render the reference into its container
    window.Scalar.createApiReference('#console-reference', config);

})();
