(function($) {

$(document).ready(function() {

    var config = {};
    config.apiPrefix = '/zato/config-db/sql/';
    config.testUrl = '/zato/config-db/sql/test';
    config.saveUrl = '/zato/config-db/sql/save';
    config.saveProgressLabel = 'Saving...';
    config.saveErrorLabel = 'Save failed';
    config.testErrorLabel = 'Test failed';

    // The default port each database type listens on
    config.defaultPorts = {
        'sqlite': '',
        'mysql': '3306',
        'postgresql': '5432',
        'oracle': '1521'
    };

    // The current values of each database, embedded by the server at render time
    var valuesElement = document.getElementById('sql-values');
    var databaseValues = JSON.parse(valuesElement.textContent);

    // ////////////////////////////////////////////////////////////////////////

    var populateForm = function(database) {
        var values = databaseValues[database];

        $('#id_display_name').val(values.display_name);
        $('#id_description').val(values.description);
        $('#id_type').val(values.type);
        $('#id_host').val(values.host);
        $('#id_port').val(values.port);
        $('#id_name').val(values.name);
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
        out.type = $('#id_type').val();
        out.host = $('#id_host').val();
        out.port = $('#id_port').val();
        out.name = $('#id_name').val();
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

    // Switching the database repopulates the whole form ..
    $('#id_database').on('change', function() {
        $.fn.zato.form_settings.clearResults();
        populateForm($(this).val());
    });

    // .. and switching the type fills in the default port for it.
    $('#id_type').on('change', function() {
        var databaseType = $(this).val();
        $('#id_port').val(config.defaultPorts[databaseType]);
    });

    // ////////////////////////////////////////////////////////////////////////

    config.buildTestPayload = function() {
        return {
            database: $('#id_database').val(),
            values: collectValues()
        };
    };

    config.buildSavePayload = function() {
        return {
            database: $('#id_database').val(),
            values: collectValues()
        };
    };

    // ////////////////////////////////////////////////////////////////////////

    config.tourSteps = [];

    config.tourSteps[0] = {};
    config.tourSteps[0].popover = {};
    config.tourSteps[0].popover.title = 'Config DB - SQL';
    config.tourSteps[0].popover.description = 'Configure the SQL databases behind the audit log and analytics screens. ' +
        'The settings are stored as environment variables in the server process.';

    config.tourSteps[1] = {};
    config.tourSteps[1].element = '#check-button';
    config.tourSteps[1].popover = {};
    config.tourSteps[1].popover.title = 'Test';
    config.tourSteps[1].popover.description = 'Connects to the database with the values from the form and runs a test query.';

    config.tourSteps[2] = {};
    config.tourSteps[2].element = '#update-button';
    config.tourSteps[2].popover = {};
    config.tourSteps[2].popover.title = 'Save';
    config.tourSteps[2].popover.description = 'Saves the connection details. New connections to this database ' +
        'will use them from now on.';

    // ////////////////////////////////////////////////////////////////////////

    // Show the first database when the page opens
    populateForm($('#id_database').val());

    $.fn.zato.form_settings.init(config);
});

})(jQuery);
