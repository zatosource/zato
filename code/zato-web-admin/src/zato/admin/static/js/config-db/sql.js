// Config DB - the SQL databases screen.
//
// One card, one tab per database, each tab a form of its own. Every field id
// carries its database as a prefix, e.g. id_audit-log_host, which is what lets
// three forms live on one page. Test and Save act on whichever tab is open.
//
// The look is the wizard kit's, the machinery is not - there are no steps to
// walk, so the tabs are the shared dashboard tabs and the two actions post the
// panel's own values straight to their endpoints.

(function($) {

$(document).ready(function() {

// ////////////////////////////////////////////////////////////////////////

var config = {};

config.testUrl = '/zato/config-db/sql/test';
config.saveUrl = '/zato/config-db/sql/save';

// What the buttons say, and what they say while a request is on its way
config.testLabel = 'Test the connection';
config.testBusyLabel = 'Testing ..';
config.saveLabel = 'Save';
config.saveBusyLabel = 'Saving ..';

// What a request that never reached its endpoint reports
config.testErrorText = 'The test could not be run';
config.saveErrorText = 'The save could not be run';

// One tab per database, each with a panel of its own
config.databases = ['audit-log', 'analytics', 'pubsub'];
config.defaultTab = 'audit-log';
config.panelPrefix = 'config-db-sql-tab-panel-';

// The fields every database has, in the order they are rendered
config.textFields = ['display_name', 'description', 'type', 'host', 'port', 'name', 'username', 'password',
    'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'];

config.checkboxFields = ['enabled', 'ssl', 'ssl_verify'];

// Fields a database keeps editable even when it is turned off - what it is called
// stays a matter of naming, not of use
config.alwaysEditableFields = ['display_name', 'description', 'enabled'];

// The default port each database type listens on
config.defaultPorts = {
    'sqlite': '',
    'mysql': '3306',
    'postgresql': '5432',
    'oracle': '1521'
};

// ////////////////////////////////////////////////////////////////////////

// The current values of each database, embedded by the server at render time
var valuesElement = document.getElementById('config-db-sql-values');
var databaseValues = JSON.parse(valuesElement.textContent);

// Which database's panel is showing - the one Test and Save act on
var currentDatabase = config.defaultTab;

var testButton = $('#config-db-sql-test');
var saveButton = $('#config-db-sql-save');
var resultElement = $('#config-db-sql-result');

// ////////////////////////////////////////////////////////////////////////

var field = function(database, name) {
    var out = $('#id_' + database + '_' + name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A database that is turned off keeps its connection details, so they are
// greyed out rather than cleared.
var applyEnabled = function(database) {

    var toggle = field(database, 'enabled');

    // Only the audit log has the switch, every other database is always in use
    if(!toggle.length) {
        return;
    }

    var needsDisable = !toggle.is(':checked');
    var panel = $('#' + config.panelPrefix + database);
    var fields = panel.find('input, select');

    for(var editableIdx = 0; editableIdx < config.alwaysEditableFields.length; editableIdx++) {
        var editableName = config.alwaysEditableFields[editableIdx];
        fields = fields.not(field(database, editableName));
    }

    fields.prop('disabled', needsDisable);
};

// ////////////////////////////////////////////////////////////////////////

var populatePanel = function(database) {

    var values = databaseValues[database];

    for(var textIdx = 0; textIdx < config.textFields.length; textIdx++) {
        var textName = config.textFields[textIdx];
        field(database, textName).val(values[textName]);
    }

    for(var checkboxIdx = 0; checkboxIdx < config.checkboxFields.length; checkboxIdx++) {
        var checkboxName = config.checkboxFields[checkboxIdx];
        field(database, checkboxName).prop('checked', values[checkboxName]);
    }

    applyEnabled(database);
};

// ////////////////////////////////////////////////////////////////////////

var collectValues = function(database) {

    var out = {};

    for(var textIdx = 0; textIdx < config.textFields.length; textIdx++) {
        var textName = config.textFields[textIdx];
        out[textName] = field(database, textName).val();
    }

    for(var checkboxIdx = 0; checkboxIdx < config.checkboxFields.length; checkboxIdx++) {
        var checkboxName = config.checkboxFields[checkboxIdx];
        out[checkboxName] = field(database, checkboxName).is(':checked');
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whatever the last test or save said is no longer about what is on screen
var clearVerdict = function() {
    resultElement.text('');
    resultElement.removeClass('wizard-probe-ok wizard-probe-error');
};

var paintVerdict = function(isOk, text) {
    resultElement.text(text);
    resultElement.toggleClass('wizard-probe-ok', isOk);
    resultElement.toggleClass('wizard-probe-error', !isOk);
};

// ////////////////////////////////////////////////////////////////////////

// Both endpoints answer with a message on success and an error on failure,
// the failure arriving as a 500 with the same JSON body.
var errorTextFromResponse = function(xhr, fallbackText) {

    var out = fallbackText;

    try {
        var response = JSON.parse(xhr.responseText);
        if(response.error) {
            out = response.error;
        }
    }
    catch(ignored) {
        if(xhr.responseText) {
            out = xhr.responseText;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One request for both actions - what differs is the endpoint, what the button
// says while it runs and what a request that never got through reports.
var runAction = function(spec) {

    // An action already on its way is left to finish
    if(spec.button.prop('disabled')) {
        return;
    }

    clearVerdict();

    spec.button.prop('disabled', true);
    spec.button.text(spec.busyLabel);

    var finish = function() {
        spec.button.prop('disabled', false);
        spec.button.text(spec.label);
    };

    $.ajax({
        url: spec.url,
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            database: currentDatabase,
            values: collectValues(currentDatabase)
        }),
        contentType: 'application/json',
        success: function(response) {
            finish();
            paintVerdict(true, response.message);
        },
        error: function(xhr) {
            finish();
            paintVerdict(false, errorTextFromResponse(xhr, spec.errorText));
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

testButton.on('click', function() {
    runAction({
        button: testButton,
        url: config.testUrl,
        label: config.testLabel,
        busyLabel: config.testBusyLabel,
        errorText: config.testErrorText
    });
});

saveButton.on('click', function() {
    runAction({
        button: saveButton,
        url: config.saveUrl,
        label: config.saveLabel,
        busyLabel: config.saveBusyLabel,
        errorText: config.saveErrorText
    });
});

// ////////////////////////////////////////////////////////////////////////

// Switching the type fills in the default port for it ..
$('.config-db-sql-type').on('change', function() {

    var select = $(this);
    var databaseType = select.val();
    var panel = select.closest('.dashboard-tab-panel');

    panel.find('input[id$="_port"]').val(config.defaultPorts[databaseType]);
});

// .. and turning the audit log off greys its own fields out.
$('input[id$="_enabled"]').on('change', function() {

    var panel = $(this).closest('.dashboard-tab-panel');
    var database = panel.attr('id').substring(config.panelPrefix.length);

    applyEnabled(database);
});

// ////////////////////////////////////////////////////////////////////////

// What each field of a panel is for. The map is written once, in field names,
// and then handed to the help mode once per database, under that database's
// own ids - the three panels ask the same questions.
var fieldDescriptions = {
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

var buildHelpDescriptions = function() {

    var out = {};

    for(var databaseIdx = 0; databaseIdx < config.databases.length; databaseIdx++) {

        var database = config.databases[databaseIdx];

        for(var fieldName in fieldDescriptions) {
            out['id_' + database + '_' + fieldName] = fieldDescriptions[fieldName];
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every panel shows its own database's values from the moment the page opens ..
for(var databaseIdx = 0; databaseIdx < config.databases.length; databaseIdx++) {
    populatePanel(config.databases[databaseIdx]);
}

// .. a tab both opens a panel and picks what Test and Save act on ..
var onTabChange = function(database) {
    currentDatabase = database;
    clearVerdict();
};

$.fn.zato.dashboard_kit.tabs.init({
    tab_selector: '#config-db-sql-tabs .dashboard-tab',
    panel_prefix: config.panelPrefix,
    default_tab: config.defaultTab,
    on_change: onTabChange
});

// .. the help mode walks the rows of whichever panel is open ..
$.fn.zato.how_it_works.init({
    badgeId: 'config-db-sql-how-it-works',
    divId: '#config-db-sql',
    fieldSelector: '.wizard-name-row, .wizard-field-row, .wizard-toggle-row',

    // The card has empty margin on its left, so the tooltips go there
    // instead of covering the rows above the described field
    placement: 'left',
    descriptions: buildHelpDescriptions()
});

// .. and the page is shown once it is fully filled in.
$.fn.zato.dashboard_kit.reveal();

// ////////////////////////////////////////////////////////////////////////

});

})(jQuery);
