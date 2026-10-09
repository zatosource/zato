
// The Config tab of the SMS dialogs - the provider account, the sender, the delivery reports, the pool and the timeout
// of an outgoing connection, and the receiving mode of a channel, each edited in a popover of its own.

$.fn.zato.sms.config = {

    idPrefix: 'sms-tab',
    idPrefixDjango: 'id_',

    popoverClass: 'sms-tab-popover',
    popupClass: 'alerts-tab-micro-form',

    // The dialog's own How does it work? badge covers the tab
    showHowItWorks: false,

    // The popovers open inside a dialog, so their buttons are the dialog's plain ones
    doneButtonClass: '',
    otherButtonClass: '',

    fieldName: 'name',
    fieldProvider: 'provider',
    fieldHost: 'host',
    fieldUsername: 'username',
    fieldSecret: 'secret',
    fieldSignatureSecret: 'signature_secret',
    fieldSender: 'sender',
    fieldChannelName: 'channel_name',
    fieldPoolSize: 'pool_size',
    fieldTimeout: 'timeout',
    fieldReceiveMode: 'receive_mode',
    fieldRunEvery: 'scheduler_run_every',
    fieldRunUnit: 'scheduler_run_unit',

    // The suffix of the unit select of a count of seconds
    unitFieldSuffix: '_unit',

    accountLine: 'account',
    senderLine: 'sender',
    reportsLine: 'reports',
    poolLine: 'pool',
    receiveLine: 'receive',

    // Each provider's credential labels
    providerLabels: {
        'twilio': {username: 'Account SID', password: 'Auth token'},
        'vonage': {username: 'API key', password: 'API secret'},
        'infobip': {username: 'Username', password: 'API key'},
        'africas-talking': {username: 'Username', password: 'API key'},
    },

    accountTitle: 'Provider account',
    senderTitle: 'Sender',
    reportsTitle: 'Delivery reports',
    poolTitle: 'Pool and timeout',
    receiveTitle: 'Receiving',

    labelProvider: 'Provider',
    labelHost: 'Host',
    labelHostRequired: 'Host (required)',
    labelSignatureSecret: 'Signature secret',
    labelSender: 'Number or sender ID',
    labelChannelName: 'Report to channel',
    labelPoolSize: 'Connections',
    labelTimeout: 'Timeout',
    labelReceiveMode: 'Mode',
    labelRunEvery: 'Poll every',

    summaryAccount: '{provider} - {username}',
    summaryAccountNoUsername: '{provider} - no account yet',
    summarySenderNone: 'Not set yet',
    summaryReportsChannel: 'To channel {channel}',
    summaryReportsNone: 'No channel',
    summaryPool: '{connections}, {timeout} timeout',
    summaryWebhook: 'Webhook at {path}',
    summaryPolling: 'Polling every {interval}',

    connectionSingular: 'connection',
    connectionPlural: 'connections',

    helpAccount: 'The provider the messages go through and the account they go through it with. ' +
        'The secrets are stored encrypted and never shown again, left empty they keep their current values.',
    helpProvider: 'The SMS provider the connection sends through. The labels of the credentials follow it.',
    helpHost: 'The provider\'s API address. Each provider has a default except Infobip, whose address is specific to the account.',
    helpUsername: 'The account identifier the provider authenticates the connection with.',
    helpSecret: 'The secret the provider authenticates the connection with. ' +
        'Stored encrypted and never shown again, leave it empty to keep the current one.',
    helpSignatureSecret: 'The Vonage signature secret that incoming callbacks are verified with. ' +
        'Stored encrypted and never shown again, leave it empty to keep the current one.',
    helpSender: 'The number or alphanumeric sender ID messages are sent from, unless a service names another one.',
    helpReports: 'The SMS channel whose webhook URL each message names as its status callback, ' +
        'so that delivery reports reach that channel.',
    helpPool: 'How many HTTP connections to the provider are kept open at most and how long a request may take ' +
        'before it is given up.',
    helpPoolSize: 'How many HTTP connections to the provider are kept open at most.',
    helpTimeout: 'How long a request to the provider may take before it is given up.',
    helpReceive: 'How messages reach the channel - the provider calls the channel\'s webhook, ' +
        'or the channel asks the provider for new messages on a schedule.',
    helpReceiveMode: 'Webhook - the provider calls the channel at its webhook path. Polling - the channel asks ' +
        'the provider for new messages every so often.',
    helpRunEvery: 'How often a polling channel asks the provider for new messages.'
};

$.fn.zato.sms.state = {
    panelId: null,
    fieldPrefix: '',

    // Whether the bound form is an outgoing connection's, with reports and a pool, or a channel's, with a receiving mode
    isOutgoing: true,

    // The provider data of the page, read once off its json_script element
    serverConfig: null
};

// The micro-forms kit installs the popover engine here
$.fn.zato.sms.forms = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.sms.init = function(options) {

    var tab = $.fn.zato.sms;
    var config = tab.config;

    tab.state.serverConfig = JSON.parse(document.getElementById(options.config_id).textContent);

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.buildDescriptors(),
        popupClass: config.popoverClass + ' ' + config.popupClass,
        showHowItWorks: config.showHowItWorks,
        doneButtonClass: config.doneButtonClass,
        otherButtonClass: config.otherButtonClass,
        showCancel: true,
        onDone: tab.render
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The descriptors of the micro-forms - the ones the bound form has are opened, the rest stay unused
$.fn.zato.sms.buildDescriptors = function() {

    var tab = $.fn.zato.sms;
    var config = tab.config;
    var labels = config.providerLabels[tab.state.serverConfig.providers[0]];
    var out = {};

    out[config.accountLine] = {
        title: config.accountTitle,
        pages: [[
            {field: config.fieldProvider, label: config.labelProvider, kind: 'select'},
            {field: config.fieldHost, label: config.labelHost, kind: 'text'},
            {field: config.fieldUsername, label: labels.username, kind: 'text'},
            {field: config.fieldSecret, label: labels.password, kind: 'password'},
            {field: config.fieldSignatureSecret, label: config.labelSignatureSecret, kind: 'password'}
        ]]
    };

    out[config.senderLine] = {
        title: config.senderTitle,
        pages: [[
            {field: config.fieldSender, label: config.labelSender, kind: 'text'}
        ]]
    };

    out[config.reportsLine] = {
        title: config.reportsTitle,
        pages: [[
            {field: config.fieldChannelName, label: config.labelChannelName, kind: 'select'}
        ]]
    };

    out[config.poolLine] = {
        title: config.poolTitle,
        fitContent: true,
        pages: [[
            [
                {field: config.fieldPoolSize, label: config.labelPoolSize, kind: 'number'},
                {field: config.fieldTimeout, label: config.labelTimeout, kind: 'number', unitField: tab.unitField(config.fieldTimeout)}
            ]
        ]]
    };

    out[config.receiveLine] = {
        title: config.receiveTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldReceiveMode, label: config.labelReceiveMode, kind: 'select'},
            {field: config.fieldRunEvery, label: config.labelRunEvery, kind: 'number', unitField: config.fieldRunUnit}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The name of the unit select of a count of seconds
$.fn.zato.sms.unitField = function(fieldName) {
    var out = fieldName + $.fn.zato.sms.config.unitFieldSuffix;
    return out;
}

// A count as the form holds it, with its unit
$.fn.zato.sms.durationText = function(fieldName, unitFieldName) {

    var tab = $.fn.zato.sms;
    var count = parseInt(tab.field(fieldName).val());
    var unitSelect = tab.field(unitFieldName);
    var singular = unitSelect.val();
    var plural = unitSelect.find('option:selected').text();

    var out = $.fn.zato.count_text(count, singular, plural);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The DOM id of one of the tab's fields
$.fn.zato.sms.fieldId = function(fieldName) {
    var tab = $.fn.zato.sms;
    var out = tab.config.idPrefixDjango + tab.state.fieldPrefix + fieldName;
    return out;
}

// One of the tab's fields
$.fn.zato.sms.field = function(fieldName) {
    var out = $('#' + $.fn.zato.sms.fieldId(fieldName));
    return out;
}

// The id of one element of the bound panel
$.fn.zato.sms.elementId = function(part, lineName) {
    var out = $.fn.zato.sms.state.panelId + '-' + part + '-' + lineName;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the popovers' inputs
$.fn.zato.sms.helpDescriptions = function() {

    var tab = $.fn.zato.sms;
    var config = tab.config;
    var out = {};

    out[tab.forms.inputId(config.fieldProvider)] = config.helpProvider;
    out[tab.forms.inputId(config.fieldHost)] = config.helpHost;
    out[tab.forms.inputId(config.fieldUsername)] = config.helpUsername;
    out[tab.forms.inputId(config.fieldSecret)] = config.helpSecret;
    out[tab.forms.inputId(config.fieldSignatureSecret)] = config.helpSignatureSecret;
    out[tab.forms.inputId(config.fieldSender)] = config.helpSender;
    out[tab.forms.inputId(config.fieldChannelName)] = config.helpReports;
    out[tab.forms.inputId(config.fieldPoolSize)] = config.helpPoolSize;
    out[tab.forms.inputId(config.fieldTimeout)] = config.helpTimeout;
    out[tab.forms.inputId(config.fieldReceiveMode)] = config.helpReceiveMode;
    out[tab.forms.inputId(config.fieldRunEvery)] = config.helpRunEvery;

    return out;
}

// The how-it-works texts of the lines
$.fn.zato.sms.descriptions = function() {

    var tab = $.fn.zato.sms;
    var config = tab.config;
    var out = {};

    out[tab.elementId('edit', config.accountLine)] = config.helpAccount;
    out[tab.elementId('edit', config.senderLine)] = config.helpSender;
    out[tab.elementId('edit', config.reportsLine)] = config.helpReports;
    out[tab.elementId('edit', config.poolLine)] = config.helpPool;
    out[tab.elementId('edit', config.receiveLine)] = config.helpReceive;

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The summary of the account line
$.fn.zato.sms.formatAccountSummary = function() {

    var tab = $.fn.zato.sms;
    var config = tab.config;
    var provider = tab.field(config.fieldProvider).val();
    var providerHuman = tab.state.serverConfig.provider_human[provider];
    var username = tab.field(config.fieldUsername).val();
    var out;

    if(username === '') {
        out = config.summaryAccountNoUsername.replace('{provider}', providerHuman);
    }
    else {
        out = config.summaryAccount.replace('{provider}', providerHuman).replace('{username}', username);
    }

    return out;
}

// The summary of the sender line
$.fn.zato.sms.formatSenderSummary = function() {

    var tab = $.fn.zato.sms;
    var out = tab.field(tab.config.fieldSender).val();

    if(out === '') {
        out = tab.config.summarySenderNone;
    }

    return out;
}

// The summary of the delivery reports line
$.fn.zato.sms.formatReportsSummary = function() {

    var tab = $.fn.zato.sms;
    var channelName = tab.field(tab.config.fieldChannelName).val();
    var out;

    if(channelName === '' || channelName === null) {
        out = tab.config.summaryReportsNone;
    }
    else {
        out = tab.config.summaryReportsChannel.replace('{channel}', channelName);
    }

    return out;
}

// The summary of the pool line
$.fn.zato.sms.formatPoolSummary = function() {

    var tab = $.fn.zato.sms;
    var config = tab.config;
    var poolSize = parseInt(tab.field(config.fieldPoolSize).val());

    var out = config.summaryPool
        .replace('{connections}', $.fn.zato.count_text(poolSize, config.connectionSingular, config.connectionPlural))
        .replace('{timeout}', tab.durationText(config.fieldTimeout, tab.unitField(config.fieldTimeout)));

    return out;
}

// The summary of the receiving line
$.fn.zato.sms.formatReceiveSummary = function() {

    var tab = $.fn.zato.sms;
    var config = tab.config;
    var serverConfig = tab.state.serverConfig;
    var receiveMode = tab.field(config.fieldReceiveMode).val();
    var out;

    if(receiveMode === serverConfig.receive_mode_polling) {
        out = config.summaryPolling.replace('{interval}', tab.durationText(config.fieldRunEvery, config.fieldRunUnit));
    }
    else {
        var path = serverConfig.webhook_path_prefix + tab.field(config.fieldName).val();
        out = config.summaryWebhook.replace('{path}', path);
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Renders the bound panel from the form
$.fn.zato.sms.render = function() {

    var tab = $.fn.zato.sms;
    var config = tab.config;

    document.getElementById(tab.elementId('summary', config.accountLine)).textContent = tab.formatAccountSummary();
    document.getElementById(tab.elementId('summary', config.senderLine)).textContent = tab.formatSenderSummary();

    if(tab.state.isOutgoing) {
        document.getElementById(tab.elementId('summary', config.reportsLine)).textContent = tab.formatReportsSummary();
        document.getElementById(tab.elementId('summary', config.poolLine)).textContent = tab.formatPoolSummary();
    }
    else {
        document.getElementById(tab.elementId('summary', config.receiveLine)).textContent = tab.formatReceiveSummary();
    }
}

// /////////////////////////////////////////////////////////////////////////////

// Gives the open popover the tab's own class, under which sms-tab.css hides the fields a provider or a receiving
// mode does not need, and keeps it at the width of all its fields, so it does not resize as fields hide
$.fn.zato.sms.lockPopover = function() {

    var tab = $.fn.zato.sms;
    var forms = tab.forms;
    var popper = forms._instance.popper;

    var container = popper.querySelector('#' + forms.config.popupId);
    container.classList.add(tab.config.popoverClass);
    container.style.width = container.offsetWidth + 'px';

    var out = popper;
    return out;
}

// The label of one input of the open popover
$.fn.zato.sms.popoverLabel = function(popper, fieldName) {
    var out = popper.querySelector('label[for="' + $.fn.zato.sms.forms.inputId(fieldName) + '"]');
    return out;
}

// The field of one input of the open popover - a field on a line of its own
$.fn.zato.sms.popoverField = function(popper, fieldName) {
    var out = popper.querySelector('#' + $.fn.zato.sms.forms.inputId(fieldName)).closest('.micro-form-field');
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The credential labels, the host label and the signature secret field of the account popover follow the provider
$.fn.zato.sms.applyProvider = function(popper, shouldFillHost) {

    var tab = $.fn.zato.sms;
    var config = tab.config;
    var serverConfig = tab.state.serverConfig;

    var provider = popper.querySelector('#' + tab.forms.inputId(config.fieldProvider)).value;
    var labels = config.providerLabels[provider];

    tab.popoverLabel(popper, config.fieldUsername).textContent = labels.username;
    tab.popoverLabel(popper, config.fieldSecret).textContent = labels.password;

    var hasSignatureSecret = serverConfig.providers_with_signature_secret.indexOf(provider) !== -1;
    tab.popoverField(popper, config.fieldSignatureSecret).hidden = !hasSignatureSecret;

    var isHostRequired = serverConfig.providers_requiring_host.indexOf(provider) !== -1;
    var hostLabel = config.labelHost;
    if(isHostRequired) {
        hostLabel = config.labelHostRequired;
    }
    tab.popoverLabel(popper, config.fieldHost).textContent = hostLabel;

    // A provider change sets the provider's default host, opening the popover leaves the host unchanged
    if(shouldFillHost) {
        popper.querySelector('#' + tab.forms.inputId(config.fieldHost)).value = serverConfig.default_host[provider];
    }
}

// Opens the account popover
$.fn.zato.sms.openAccount = function(link) {

    var tab = $.fn.zato.sms;
    var config = tab.config;

    tab.forms.open(config.accountLine, link, config.fieldProvider);

    var popper = tab.lockPopover();
    var select = popper.querySelector('#' + tab.forms.inputId(config.fieldProvider));

    select.addEventListener('change', function() {
        tab.applyProvider(popper, true);
    });

    tab.applyProvider(popper, false);
}

// /////////////////////////////////////////////////////////////////////////////

// The schedule field of the receiving popover is shown for a polling channel only
$.fn.zato.sms.applyReceiveMode = function(popper) {

    var tab = $.fn.zato.sms;
    var config = tab.config;

    var receiveMode = popper.querySelector('#' + tab.forms.inputId(config.fieldReceiveMode)).value;
    var isPolling = receiveMode === tab.state.serverConfig.receive_mode_polling;

    tab.popoverField(popper, config.fieldRunEvery).hidden = !isPolling;
}

// Opens the receiving popover
$.fn.zato.sms.openReceive = function(link) {

    var tab = $.fn.zato.sms;
    var config = tab.config;

    tab.forms.open(config.receiveLine, link, config.fieldReceiveMode);

    var popper = tab.lockPopover();
    var select = popper.querySelector('#' + tab.forms.inputId(config.fieldReceiveMode));

    select.addEventListener('change', function() {
        tab.applyReceiveMode(popper);
    });

    tab.applyReceiveMode(popper);
}

// /////////////////////////////////////////////////////////////////////////////

// Opens a popover whose rows do not depend on one another
$.fn.zato.sms.bindLine = function(lineName, focusFieldName) {

    var tab = $.fn.zato.sms;

    $('#' + tab.elementId('edit', lineName)).off('click.sms_tab').on('click.sms_tab', function() {
        tab.forms.open(lineName, this, focusFieldName);
        tab.lockPopover();
    });
}

// Binds one form's panel, before the dialog opens
$.fn.zato.sms.bind = function(options) {

    var tab = $.fn.zato.sms;
    var config = tab.config;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;
    tab.state.isOutgoing = options.is_outgoing;

    $('#' + tab.elementId('edit', config.accountLine)).off('click.sms_tab').on('click.sms_tab', function() {
        tab.openAccount(this);
    });

    tab.bindLine(config.senderLine, config.fieldSender);

    if(tab.state.isOutgoing) {
        tab.bindLine(config.reportsLine, config.fieldChannelName);
        tab.bindLine(config.poolLine, config.fieldPoolSize);
    }
    else {
        $('#' + tab.elementId('edit', config.receiveLine)).off('click.sms_tab').on('click.sms_tab', function() {
            tab.openReceive(this);
        });

        // The webhook path follows the channel's name
        tab.field(config.fieldName).off('input.sms_tab').on('input.sms_tab', tab.render);
    }

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
