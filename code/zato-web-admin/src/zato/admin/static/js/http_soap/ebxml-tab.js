
// The ebXML tab of the create form of a SOAP channel or a SOAP outgoing connection.

$.fn.zato.http_soap.ebxml = {};

$.fn.zato.http_soap.ebxml.config = {

    idPrefix: 'ebxml-tab',
    fieldIdPrefix: 'id_ebxml_',

    popoverClass: 'ebxml-tab-popover',
    popupClass: 'alerts-tab-micro-form',
    showHowItWorks: false,

    agreementsLine: 'agreements',
    signingLine: 'signing',

    fieldAgreement: 'agreement',
    fieldSigningCertificate: 'signing_certificate',

    agreementsTitle: 'Agreements',
    signingTitle: 'Signing certificate',

    labelAgreement: 'Agreement',
    labelSigningCertificate: 'Local signing certificate'
};

$.fn.zato.http_soap.ebxml.state = {
    panelId: null
};

// The micro-forms kit installs the popover engine here
$.fn.zato.http_soap.ebxml.forms = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebxml.field = function(fieldName) {
    var out = $('#' + $.fn.zato.http_soap.ebxml.config.fieldIdPrefix + fieldName);
    return out;
}

$.fn.zato.http_soap.ebxml.helpDescriptions = function() {
    var out = {};
    return out;
}

$.fn.zato.http_soap.ebxml.elementId = function(part, lineName) {
    var out = $.fn.zato.http_soap.ebxml.state.panelId + '-' + part + '-' + lineName;
    return out;
}

$.fn.zato.http_soap.ebxml.optionText = function(fieldName) {
    var out = $.fn.zato.http_soap.ebxml.field(fieldName).find('option:selected').text();
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebxml.buildDescriptors = function() {

    var config = $.fn.zato.http_soap.ebxml.config;
    var out = {};

    out[config.agreementsLine] = {
        title: config.agreementsTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldAgreement, label: config.labelAgreement, kind: 'select'}
        ]]
    };

    out[config.signingLine] = {
        title: config.signingTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldSigningCertificate, label: config.labelSigningCertificate, kind: 'select'}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebxml.render = function() {

    var tab = $.fn.zato.http_soap.ebxml;
    var config = tab.config;

    var agreements = tab.optionText(config.fieldAgreement);
    var signing = tab.optionText(config.fieldSigningCertificate);

    document.getElementById(tab.elementId('summary', config.agreementsLine)).textContent = agreements;
    document.getElementById(tab.elementId('summary', config.signingLine)).textContent = signing;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.ebxml.init = function(options) {

    var tab = $.fn.zato.http_soap.ebxml;
    var config = tab.config;

    tab.state.panelId = options.panel_id;

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.buildDescriptors(),
        popupClass: config.popoverClass + ' ' + config.popupClass,
        showHowItWorks: config.showHowItWorks,
        showCancel: true,
        onDone: tab.render
    });

    var lines = [
        [config.agreementsLine, config.fieldAgreement],
        [config.signingLine, config.fieldSigningCertificate]
    ];

    lines.forEach(function(line) {
        var lineName = line[0];
        var focusField = line[1];

        $('#' + tab.elementId('edit', lineName)).on('click', function() {
            tab.forms.open(lineName, this, focusField);
        });
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
