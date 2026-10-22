// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// The ebMS tab of a SOAP channel's create form - its decision lines, the micro-forms they open and their summaries.
// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebms_tab = {};

$.fn.zato.http_soap.ebms_tab.config = {

    idPrefix: 'ebms-tab',
    fieldIdPrefix: 'ebms-tab-field-',

    popoverClass: 'ebms-tab-popover',
    popupClass: 'alerts-tab-micro-form',

    showHowItWorks: false,
    doneButtonClass: '',
    otherButtonClass: '',

    // The Main tab's security select, whose definitions the signatures pick from
    securitySelectId: 'id_security',

    unitFieldSuffix: '_unit',

    lineCpaFile: 'cpa_file',
    lineAgreement: 'agreement',
    lineHostParty: 'host_party',
    linePartnerParty: 'partner_party',
    lineActions: 'actions',
    lineSignatures: 'signatures',
    lineAcknowledgments: 'acknowledgments',
    lineDuplicates: 'duplicates',

    fieldCpaFile: 'cpa_file',
    fieldCpaId: 'cpa_id',
    fieldHostPartyId: 'host_party_id',
    fieldHostPartyIdType: 'host_party_id_type',
    fieldHostRole: 'host_role',
    fieldPartnerPartyId: 'partner_party_id',
    fieldPartnerPartyIdType: 'partner_party_id_type',
    fieldPartnerRole: 'partner_role',
    fieldServiceFilter: 'service_filter',
    fieldActionFilter: 'action_filter',
    fieldVerifySignature: 'verify_signature',
    fieldSignatureDefinition: 'signature_definition',
    fieldKeySource: 'key_source',
    fieldSignatureAlgorithm: 'signature_algorithm',
    fieldDigestAlgorithm: 'digest_algorithm',
    fieldCanonicalization: 'canonicalization',
    fieldMinKeySize: 'min_key_size',
    fieldAckMode: 'ack_mode',
    fieldAckUrl: 'ack_url',
    fieldSignAck: 'sign_ack',
    fieldDuplicateElimination: 'duplicate_elimination',
    fieldRetention: 'retention',

    ackModeAsync: 'async',
    ackModeNone: 'none',

    titleAgreement: 'Agreement',
    titleHostParty: 'Our party',
    titlePartnerParty: 'Partner',
    titleActions: 'Accepted actions',
    titleSignatures: 'Signatures',
    titleAcknowledgments: 'Acknowledgments',
    titleDuplicates: 'Duplicate elimination',

    labelCpaId: 'CPA ID',
    labelPartyId: 'Party ID',
    labelPartyIdType: 'Type',
    labelRole: 'Role',
    labelService: 'eb:Service',
    labelAction: 'eb:Action',
    labelVerifySignature: 'Verify signatures',
    labelSignatureDefinition: 'WS-Security definition',
    labelKeySource: 'Signer key',
    labelSignatureAlgorithm: 'Signature algorithm',
    labelDigestAlgorithm: 'Digest algorithm',
    labelCanonicalization: 'Canonicalization',
    labelMinKeySize: 'Minimum key size',
    labelAckMode: 'Mode',
    labelAckUrl: 'URL',
    labelSignAck: 'Sign',
    labelDuplicateElimination: 'Eliminate duplicates',
    labelRetention: 'Keep message IDs for',

    placeholderAny: 'Any',

    summaryNoCpaFile: 'No file',
    summaryNoCpaId: 'Not set',
    summaryNoParty: 'Not set',
    summaryParty: '{id} ({type}), {role}',
    summaryPartyNoRole: '{id} ({type})',
    summaryAnyService: 'Any service',
    summaryAnyAction: 'any action',
    summaryActions: '{service}, {action}',
    summaryNotVerified: 'Not verified',
    summarySignatures: '{signature} with {digest}, {canonicalization}, {definition}',
    summaryNoDefinition: 'no definition picked yet',
    summaryAckNone: 'None',
    summaryAckSync: 'Synchronous',
    summaryAckAsync: 'Asynchronous to {url}',
    summaryAckAsyncNoUrl: 'Asynchronous, no URL yet',
    summaryAckSigned: '{mode}, signed',
    summaryDuplicatesOff: 'Off',
    summaryDuplicates: 'Message IDs kept for {retention}'
};

$.fn.zato.http_soap.ebms_tab.state = {
    panelId: null
};

// The micro-forms kit installs the popover engine here
$.fn.zato.http_soap.ebms_tab.forms = {};

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebms_tab.init = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;

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

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// A party is the same three fields whichever side it stands on
$.fn.zato.http_soap.ebms_tab.partyDescriptor = function(title, idField, typeField, roleField) {

    var config = $.fn.zato.http_soap.ebms_tab.config;

    var out = {
        title: title,
        fitContent: true,
        pages: [[
            [
                {field: idField, label: config.labelPartyId, kind: 'text'},
                {field: typeField, label: config.labelPartyIdType, kind: 'select'}
            ],
            {field: roleField, label: config.labelRole, kind: 'text'}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebms_tab.buildDescriptors = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;
    var out = {};

    out[config.lineAgreement] = {
        title: config.titleAgreement,
        fitContent: true,
        pages: [[
            {field: config.fieldCpaId, label: config.labelCpaId, kind: 'text'}
        ]]
    };

    out[config.lineHostParty] = tab.partyDescriptor(config.titleHostParty,
        config.fieldHostPartyId, config.fieldHostPartyIdType, config.fieldHostRole);

    out[config.linePartnerParty] = tab.partyDescriptor(config.titlePartnerParty,
        config.fieldPartnerPartyId, config.fieldPartnerPartyIdType, config.fieldPartnerRole);

    out[config.lineActions] = {
        title: config.titleActions,
        fitContent: true,
        pages: [[
            [
                {field: config.fieldServiceFilter, label: config.labelService, kind: 'text', placeholder: config.placeholderAny},
                {field: config.fieldActionFilter, label: config.labelAction, kind: 'text', placeholder: config.placeholderAny}
            ]
        ]]
    };

    out[config.lineSignatures] = {
        title: config.titleSignatures,
        fitContent: true,
        pages: [[
            {field: config.fieldVerifySignature, label: config.labelVerifySignature, kind: 'checkbox'},
            [
                {field: config.fieldSignatureDefinition, label: config.labelSignatureDefinition, kind: 'select'},
                {field: config.fieldKeySource, label: config.labelKeySource, kind: 'select'}
            ],
            [
                {field: config.fieldSignatureAlgorithm, label: config.labelSignatureAlgorithm, kind: 'select'},
                {field: config.fieldDigestAlgorithm, label: config.labelDigestAlgorithm, kind: 'select'}
            ],
            [
                {field: config.fieldCanonicalization, label: config.labelCanonicalization, kind: 'select'},
                {field: config.fieldMinKeySize, label: config.labelMinKeySize, kind: 'select'}
            ]
        ]]
    };

    out[config.lineAcknowledgments] = {
        title: config.titleAcknowledgments,
        fitContent: true,
        pages: [[
            [
                {field: config.fieldAckMode, label: config.labelAckMode, kind: 'select'},
                {field: config.fieldSignAck, label: config.labelSignAck, kind: 'checkbox', labelAbove: true}
            ],
            {field: config.fieldAckUrl, label: config.labelAckUrl, kind: 'text'}
        ]]
    };

    out[config.lineDuplicates] = {
        title: config.titleDuplicates,
        fitContent: true,
        pages: [[
            {field: config.fieldDuplicateElimination, label: config.labelDuplicateElimination, kind: 'checkbox'},
            {field: config.fieldRetention, label: config.labelRetention, kind: 'number', unitField: tab.unitField(config.fieldRetention)}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// One of the tab's fields
$.fn.zato.http_soap.ebms_tab.field = function(fieldName) {
    var out = $('#' + $.fn.zato.http_soap.ebms_tab.config.fieldIdPrefix + fieldName);
    return out;
}

// The id of one element of the bound panel
$.fn.zato.http_soap.ebms_tab.elementId = function(part, lineName) {
    var out = $.fn.zato.http_soap.ebms_tab.state.panelId + '-' + part + '-' + lineName;
    return out;
}

$.fn.zato.http_soap.ebms_tab.unitField = function(fieldName) {
    var out = fieldName + $.fn.zato.http_soap.ebms_tab.config.unitFieldSuffix;
    return out;
}

// The popovers have no help badge, so there is nothing to describe
$.fn.zato.http_soap.ebms_tab.helpDescriptions = function() {
    var out = {};
    return out;
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The label of the option a select of the tab has picked
$.fn.zato.http_soap.ebms_tab.selectedText = function(fieldName) {
    var out = $.fn.zato.http_soap.ebms_tab.field(fieldName).find('option:selected').text();
    return out;
}

$.fn.zato.http_soap.ebms_tab.isChecked = function(fieldName) {
    var out = $.fn.zato.http_soap.ebms_tab.field(fieldName).is(':checked');
    return out;
}

$.fn.zato.http_soap.ebms_tab.textValue = function(fieldName) {
    var out = $.fn.zato.http_soap.ebms_tab.field(fieldName).val().trim();
    return out;
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebms_tab.formatCpaFile = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var files = tab.field(tab.config.fieldCpaFile)[0].files;
    var out;

    if(files.length === 0) {
        out = tab.config.summaryNoCpaFile;
    }
    else {
        var file = files[0];
        out = file.name;
    }

    return out;
}

$.fn.zato.http_soap.ebms_tab.formatAgreement = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var out = tab.textValue(tab.config.fieldCpaId);

    if(out === '') {
        out = tab.config.summaryNoCpaId;
    }

    return out;
}

$.fn.zato.http_soap.ebms_tab.formatParty = function(idField, typeField, roleField) {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;

    var partyId = tab.textValue(idField);
    var role = tab.textValue(roleField);
    var partyType = tab.selectedText(typeField);
    var out;

    if(partyId === '') {
        out = config.summaryNoParty;
    }
    else if(role === '') {
        out = config.summaryPartyNoRole.replace('{id}', partyId).replace('{type}', partyType);
    }
    else {
        out = config.summaryParty.replace('{id}', partyId).replace('{type}', partyType).replace('{role}', role);
    }

    return out;
}

$.fn.zato.http_soap.ebms_tab.formatActions = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;

    var service = tab.textValue(config.fieldServiceFilter);
    var action = tab.textValue(config.fieldActionFilter);

    if(service === '') {
        service = config.summaryAnyService;
    }

    if(action === '') {
        action = config.summaryAnyAction;
    }

    var out = config.summaryActions.replace('{service}', service).replace('{action}', action);
    return out;
}

$.fn.zato.http_soap.ebms_tab.formatSignatures = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;
    var out;

    if(!tab.isChecked(config.fieldVerifySignature)) {
        out = config.summaryNotVerified;
    }
    else {
        var definition = tab.field(config.fieldSignatureDefinition).val();
        var definitionText;

        if(definition === '') {
            definitionText = config.summaryNoDefinition;
        }
        else {
            definitionText = tab.selectedText(config.fieldSignatureDefinition);
        }

        out = config.summarySignatures
            .replace('{signature}', tab.selectedText(config.fieldSignatureAlgorithm))
            .replace('{digest}', tab.selectedText(config.fieldDigestAlgorithm))
            .replace('{canonicalization}', tab.selectedText(config.fieldCanonicalization))
            .replace('{definition}', definitionText);
    }

    return out;
}

$.fn.zato.http_soap.ebms_tab.formatAcknowledgments = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;
    var mode = tab.field(config.fieldAckMode).val();
    var out;

    if(mode === config.ackModeNone) {
        out = config.summaryAckNone;
    }
    else {
        if(mode === config.ackModeAsync) {
            var url = tab.textValue(config.fieldAckUrl);

            if(url === '') {
                out = config.summaryAckAsyncNoUrl;
            }
            else {
                out = config.summaryAckAsync.replace('{url}', url);
            }
        }
        else {
            out = config.summaryAckSync;
        }

        if(tab.isChecked(config.fieldSignAck)) {
            out = config.summaryAckSigned.replace('{mode}', out);
        }
    }

    return out;
}

$.fn.zato.http_soap.ebms_tab.formatDuplicates = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;
    var out;

    if(!tab.isChecked(config.fieldDuplicateElimination)) {
        out = config.summaryDuplicatesOff;
    }
    else {
        var count = parseInt(tab.field(config.fieldRetention).val());
        var unitSelect = tab.field(tab.unitField(config.fieldRetention));
        var singular = unitSelect.val();
        var plural = unitSelect.find('option:selected').text();
        var retention = $.fn.zato.count_text(count, singular, plural);

        out = config.summaryDuplicates.replace('{retention}', retention);
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebms_tab.setSummary = function(lineName, text) {
    var summary = document.getElementById($.fn.zato.http_soap.ebms_tab.elementId('summary', lineName));
    summary.textContent = text;
}

// Renders the bound panel from its fields
$.fn.zato.http_soap.ebms_tab.render = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;

    tab.setSummary(config.lineCpaFile, tab.formatCpaFile());
    tab.setSummary(config.lineAgreement, tab.formatAgreement());
    tab.setSummary(config.lineHostParty, tab.formatParty(config.fieldHostPartyId, config.fieldHostPartyIdType, config.fieldHostRole));
    tab.setSummary(config.linePartnerParty, tab.formatParty(config.fieldPartnerPartyId, config.fieldPartnerPartyIdType,
        config.fieldPartnerRole));
    tab.setSummary(config.lineActions, tab.formatActions());
    tab.setSummary(config.lineSignatures, tab.formatSignatures());
    tab.setSummary(config.lineAcknowledgments, tab.formatAcknowledgments());
    tab.setSummary(config.lineDuplicates, tab.formatDuplicates());
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The signatures pick from the same security definitions the Main tab lists
$.fn.zato.http_soap.ebms_tab.copySecurityOptions = function() {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var target = tab.field(tab.config.fieldSignatureDefinition);

    target.empty();

    $('#' + tab.config.securitySelectId).find('option').each(function() {
        var option = document.createElement('option');
        option.value = this.value;
        option.textContent = this.textContent;
        target.append(option);
    });
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Binds the create form's panel, before the dialog opens
$.fn.zato.http_soap.ebms_tab.bind = function(options) {

    var tab = $.fn.zato.http_soap.ebms_tab;
    var config = tab.config;

    tab.state.panelId = options.panel_id;

    tab.copySecurityOptions();

    // Each line opens its own micro-form, the CPA line opens the browser's file picker instead
    var popoverLines = [
        config.lineAgreement,
        config.lineHostParty,
        config.linePartnerParty,
        config.lineActions,
        config.lineSignatures,
        config.lineAcknowledgments,
        config.lineDuplicates
    ];

    popoverLines.forEach(function(lineName) {
        $('#' + tab.elementId('edit', lineName)).off('click.ebms_tab').on('click.ebms_tab', function() {
            tab.forms.open(lineName, this);
        });
    });

    var cpaFile = tab.field(config.fieldCpaFile);

    $('#' + tab.elementId('edit', config.lineCpaFile)).off('click.ebms_tab').on('click.ebms_tab', function() {
        cpaFile.click();
    });

    cpaFile.off('change.ebms_tab').on('change.ebms_tab', tab.render);

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
