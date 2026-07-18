(function($) {

$(document).ready(function() {

    var config = {};
    config.apiPrefix = '/zato/config-db/redis/';
    config.testUrl = '/zato/config-db/redis/test';
    config.saveUrl = '/zato/config-db/redis/save';
    config.saveProgressLabel = 'Saving...';
    config.saveErrorLabel = 'Save failed';
    config.testErrorLabel = 'Test failed';

    // The current values of the connection, embedded by the server at render time
    var valuesElement = document.getElementById('redis-values');
    var connectionValues = JSON.parse(valuesElement.textContent);

    // ////////////////////////////////////////////////////////////////////////

    var populateForm = function(values) {

        $('#id_display_name').val(values.display_name);
        $('#id_description').val(values.description);
        $('#id_host').val(values.host);
        $('#id_port').val(values.port);
        $('#id_db').val(values.db);
        $('#id_username').val(values.username);
        $('#id_password').val(values.password);
        $('#id_ssl').prop('checked', values.ssl);
        $('#id_ssl_ca_file').val(values.ssl_ca_file);
        $('#id_ssl_cert_file').val(values.ssl_cert_file);
        $('#id_ssl_key_file').val(values.ssl_key_file);
        $('#id_ssl_verify').prop('checked', values.ssl_verify);
    };

    // ////////////////////////////////////////////////////////////////////////

    var collectValues = function() {

        var out = {};

        out.display_name = $('#id_display_name').val();
        out.description = $('#id_description').val();
        out.host = $('#id_host').val();
        out.port = $('#id_port').val();
        out.db = $('#id_db').val();
        out.username = $('#id_username').val();
        out.password = $('#id_password').val();
        out.ssl = $('#id_ssl').is(':checked');
        out.ssl_ca_file = $('#id_ssl_ca_file').val();
        out.ssl_cert_file = $('#id_ssl_cert_file').val();
        out.ssl_key_file = $('#id_ssl_key_file').val();
        out.ssl_verify = $('#id_ssl_verify').is(':checked');

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    config.buildTestPayload = function() {
        return {
            values: collectValues()
        };
    };

    config.buildSavePayload = function() {
        return {
            values: collectValues()
        };
    };

    // ////////////////////////////////////////////////////////////////////////

    config.tourSteps = [];

    config.tourSteps[0] = {};
    config.tourSteps[0].popover = {};
    config.tourSteps[0].popover.title = 'Config DB - Redis';
    config.tourSteps[0].popover.description = 'Configure the default Redis connection, including SSL/TLS. ' +
        'The settings are stored as environment variables in the server process.';

    config.tourSteps[1] = {};
    config.tourSteps[1].element = '#check-button';
    config.tourSteps[1].popover = {};
    config.tourSteps[1].popover.title = 'Test';
    config.tourSteps[1].popover.description = 'Connects to the Redis server with the values from the form and pings it.';

    config.tourSteps[2] = {};
    config.tourSteps[2].element = '#update-button';
    config.tourSteps[2].popover = {};
    config.tourSteps[2].popover.title = 'Save';
    config.tourSteps[2].popover.description = 'Saves the connection details. New connections to this server ' +
        'will use them from now on.';

    // ////////////////////////////////////////////////////////////////////////

    // Show the current values when the page opens
    populateForm(connectionValues);

    $.fn.zato.form_settings.init(config);
});

})(jQuery);
