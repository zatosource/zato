
// ////////////////////////////////////////////////////////////////////////////
// Config DB - SQL databases UI
// ////////////////////////////////////////////////////////////////////////////

// One tab per database, each tab a card of its own. Every field id carries its
// database as a prefix, e.g. id_audit-log_host, which is what lets three forms
// live on one page. Test and Save act on whichever tab is open. The look and
// the machinery are the Redis screen's - the same card, rows, dimming,
// action-runner test and status-message save.

(function($) {

    var storedUrlBase = '';

    $.fn.zato.config_db.sql.config = {

        // One tab per database, each with a panel of its own
        databases: ['audit-log', 'analytics', 'pubsub'],
        default_database: 'audit-log',
        panel_prefix: 'config-db-sql-tab-panel-',

        // Which database can be turned off altogether - only the audit log can
        has_enabled: {
            'audit-log': true,
            'analytics': false,
            'pubsub': false
        },

        // The fields every database has, in the order they are rendered
        text_fields: ['display_name', 'description', 'type', 'host', 'port', 'name', 'username', 'password',
            'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'],

        checkbox_fields: ['enabled', 'ssl', 'ssl_verify'],

        // The default port each database type listens on
        default_ports: {
            'sqlite': '',
            'mysql': '3306',
            'postgresql': '5432',
            'oracle': '1521'
        },

        save_ok_message: 'OK, saved',
        save_error_message: 'Could not save',
        test_error_message: 'Could not connect',
        test_spinner_label: 'Testing ..',
        test_spinner_delay_ms: 250,
        test_details_title: 'Test connection response',
        test_ok_hold_ms: 1200,
        status_fade_delay_ms: 750,
        status_fade_duration_ms: 500
    };

    // ////////////////////////////////////////////////////////////////////////

    // Which database's panel is showing - the one Test and Save act on
    var currentDatabase = $.fn.zato.config_db.sql.config.default_database;

    // ////////////////////////////////////////////////////////////////////////

    // What each field of a panel is for. The map is written once, in field names,
    // and then handed to the help mode once per database, under that database's
    // own ids - the three panels ask the same questions.
    $.fn.zato.config_db.sql.field_descriptions = {
        'display_name':  'A short name for this connection.<br>It is what the connection is called<br>in the dashboard, nothing else reads it.',
        'description':   'What this connection is used for.<br>A note to whoever opens this screen next.',
        'enabled':       'Whether the audit log records anything at all.<br>With it off nothing is written, from the very<br>next event on, and the audit log screens<br>stay empty. No restart is needed either way.',
        'type':          'Which database engine is on the other side.<br>Picking one fills in the port it listens on.',
        'host':          'The address the database answers at.<br>Left out for SQLite, which is a file, not a server.',
        'port':          'The port the database listens on.<br>Filled in from the type, change it if yours differs.',
        'name':          'The name of the database to use.<br>For SQLite this is the path to the file instead.',
        'username':      'The user the server connects as.',
        'password':      'The password that user connects with.<br>It is stored as an environment variable,<br>never shown back on this screen.',
        'ssl':           'Whether the connection is encrypted.<br>The three files below are only read when it is on.',
        'ssl_ca_file':   'The certificate authority the database\'s<br>own certificate is checked against.',
        'ssl_cert_file': 'The client certificate this server presents,<br>for a database that asks for one.',
        'ssl_key_file':  'The private key belonging to that client certificate.',
        'ssl_verify':    'Whether the database\'s certificate is checked<br>against the CA file. Off accepts any certificate,<br>which is a test-environment setting.'
    };

    // ////////////////////////////////////////////////////////////////////////

    var field = function(database, name) {
        var out = $('#id_' + database + '_' + name);
        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The help texts are written once per field - each database's panel gets
    // its own copy, keyed by that database's own ids.
    var buildHelpDescriptions = function() {

        var config = $.fn.zato.config_db.sql.config;
        var descriptions = $.fn.zato.config_db.sql.field_descriptions;
        var out = {};

        for(var databaseIdx = 0; databaseIdx < config.databases.length; databaseIdx++) {

            var database = config.databases[databaseIdx];

            for(var fieldName in descriptions) {
                out['id_' + database + '_' + fieldName] = descriptions[fieldName];
            }
        }

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.config_db.sql.init = function(urlBase) {
        storedUrlBase = urlBase;

        var config = $.fn.zato.config_db.sql.config;

        // The current values of each database, embedded by the server at render time ..
        var valuesElement = document.getElementById('config-db-sql-values');
        var databaseValues = JSON.parse(valuesElement.textContent);

        // .. every panel shows its own database's values from the moment the page opens ..
        for(var databaseIdx = 0; databaseIdx < config.databases.length; databaseIdx++) {
            var database = config.databases[databaseIdx];
            $.fn.zato.config_db.sql.load_config(database, databaseValues[database]);
        }

        // .. the dimmable rows follow their toggles from now on ..
        $('input[id$="_ssl"], input[id$="_enabled"]').on('change', function() {
            var panel = $(this).closest('.dashboard-tab-panel');
            var panelDatabase = panel.attr('id').substring(config.panel_prefix.length);
            $.fn.zato.config_db.sql.update_row_state(panelDatabase);
        });

        // .. switching the type fills in the default port for it ..
        $('.config-db-sql-type').on('change', function() {
            var select = $(this);
            var databaseType = select.val();
            var panel = select.closest('.dashboard-tab-panel');
            panel.find('input[id$="_port"]').val(config.default_ports[databaseType]);
        });

        // .. a tab both opens a panel and picks what Test and Save act on ..
        $.fn.zato.dashboard_kit.tabs.init({
            tab_selector: '#config-db-sql-tabs .dashboard-tab',
            panel_prefix: config.panel_prefix,
            default_tab: config.default_database,
            on_change: function(database) {
                currentDatabase = database;
                $('#config-db-sql-status').removeClass('show fade status-message-success status-message-error');
            }
        });

        // .. and the help mode walks the rows of whichever panel is open.
        $.fn.zato.how_it_works.init({
            badgeId: 'config-db-sql-how-it-works',
            divId: '#config-db-sql',
            fieldSelector: '.config-db-sql-row',
            containerSelector: '#markup',
            placement: 'left',
            descriptions: buildHelpDescriptions()
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    // Dims and disables the rows whose toggles are off - the connection rows
    // follow the Enabled toggle and the TLS file rows additionally follow
    // the Use TLS toggle.
    $.fn.zato.config_db.sql.update_row_state = function(database) {

        var config = $.fn.zato.config_db.sql.config;
        var panel = $('#' + config.panel_prefix + database);

        var isEnabled = true;
        if(config.has_enabled[database]) {
            isEnabled = field(database, 'enabled').is(':checked');
        }

        var isSsl = field(database, 'ssl').is(':checked');

        panel.find('.config-db-sql-conn-option').each(function() {
            var row = $(this);

            var needsDisable = !isEnabled;
            if(row.hasClass('config-db-sql-ssl-option')) {
                needsDisable = needsDisable || !isSsl;
            }

            row.toggleClass('config-db-sql-row-disabled', needsDisable);
            row.find('input, select').prop('disabled', needsDisable);
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.config_db.sql.load_config = function(database, values) {

        var config = $.fn.zato.config_db.sql.config;

        for(var textIdx = 0; textIdx < config.text_fields.length; textIdx++) {
            var textName = config.text_fields[textIdx];
            field(database, textName).val(values[textName]);
        }

        for(var checkboxIdx = 0; checkboxIdx < config.checkbox_fields.length; checkboxIdx++) {
            var checkboxName = config.checkbox_fields[checkboxIdx];
            field(database, checkboxName).prop('checked', values[checkboxName]);
        }

        $.fn.zato.config_db.sql.update_row_state(database);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.config_db.sql.get_config = function(database) {

        var config = $.fn.zato.config_db.sql.config;
        var out = {};

        for(var textIdx = 0; textIdx < config.text_fields.length; textIdx++) {
            var textName = config.text_fields[textIdx];
            out[textName] = field(database, textName).val();
        }

        for(var checkboxIdx = 0; checkboxIdx < config.checkbox_fields.length; checkboxIdx++) {
            var checkboxName = config.checkbox_fields[checkboxIdx];
            out[checkboxName] = field(database, checkboxName).is(':checked');
        }

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.config_db.sql.extract_error = function(jqXHR, defaultMessage) {
        var out = defaultMessage;

        try {
            var response = JSON.parse(jqXHR.responseText);
            if(response.error) {
                out = response.error;
            }
            else if(response.message) {
                out = response.message;
            }
        }
        catch(e) {
            if(jqXHR.responseText) {
                out = jqXHR.responseText;
            }
        }

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // Shows a green message in the status slot and fades it out after holdMs
    $.fn.zato.config_db.sql.show_status_success = function(message, holdMs) {

        var status = $('#config-db-sql-status');
        var uiConfig = $.fn.zato.config_db.sql.config;

        status.removeClass('show fade status-message-success status-message-error');
        status.text(message).addClass('show status-message-success');

        setTimeout(function() {
            status.addClass('fade');
            setTimeout(function() {
                status.removeClass('show fade status-message-success');
            }, uiConfig.status_fade_duration_ms);
        }, holdMs);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.config_db.sql.save = function() {

        var values = $.fn.zato.config_db.sql.get_config(currentDatabase);
        var status = $('#config-db-sql-status');
        var uiConfig = $.fn.zato.config_db.sql.config;

        status.removeClass('show fade status-message-success status-message-error');

        $.ajax({
            url: storedUrlBase + '/save',
            type: 'POST',
            data: JSON.stringify({database: currentDatabase, values: values}),
            contentType: 'application/json',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                $.fn.zato.config_db.sql.show_status_success(uiConfig.save_ok_message, uiConfig.status_fade_delay_ms);
            },
            error: function(jqXHR) {
                var message = $.fn.zato.config_db.sql.extract_error(jqXHR, uiConfig.save_error_message);
                status.text(message).addClass('show status-message-error');
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.config_db.sql.parse_test_response = function(jqXHR) {

        var uiConfig = $.fn.zato.config_db.sql.config;

        // A request that never reached the server has no response text at all
        var body = jqXHR.responseText;
        if(body === undefined) {
            body = '';
        }

        var parsed = null;
        try {
            parsed = JSON.parse(body);
        }
        catch(e) {
            parsed = null;
        }

        // The test service always answers with JSON - success carries a message
        // with the response time, failure carries the database driver's error,
        // shown in full in the tooltip and again in the copyable details modal.
        if(parsed) {
            if(parsed.success) {
                return {
                    is_success: true,
                    label: parsed.message,
                    details_title: '',
                    details_body: '',
                    details_lexer: '',
                    status_code: 0
                };
            }
            return {
                is_success: false,
                label: parsed.error,
                details_title: parsed.error,
                details_body: parsed.error,
                details_lexer: '',
                status_code: 0
            };
        }

        // A non-JSON body means the request never made it to the test service
        return {
            is_success: false,
            label: uiConfig.test_error_message,
            details_title: uiConfig.test_error_message,
            details_body: body,
            details_lexer: '',
            status_code: jqXHR.status
        };
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.config_db.sql.test = function(testLink) {

        var values = $.fn.zato.config_db.sql.get_config(currentDatabase);
        var uiConfig = $.fn.zato.config_db.sql.config;

        $.fn.zato.action_runner.run({
            link_elem: testLink,
            url: storedUrlBase + '/test',
            data: JSON.stringify({database: currentDatabase, values: values}),
            spinner_label: uiConfig.test_spinner_label,
            show_delay_ms: uiConfig.test_spinner_delay_ms,
            details_modal_title: uiConfig.test_details_title,
            parse: $.fn.zato.config_db.sql.parse_test_response,

            // A successful test does not need the tippy at all - the outcome goes
            // into the green status message to the left of the link instead.
            on_success: function(instance, result) {
                instance.hide();
                instance.destroy();
                $.fn.zato.config_db.sql.show_status_success(result.label, uiConfig.test_ok_hold_ms);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
