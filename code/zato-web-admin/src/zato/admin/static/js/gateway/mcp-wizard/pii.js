// MCP gateway wizard - the PII and data masking section of step 2.
//
// One line saying how many fields are masked and whether PII is removed, with
// a chevron after it. A click on the line unfolds the fields under it - the
// data masking line, the PII removal switch and what follows it, which the
// stylesheet hides while the switch is off.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var pii = wizard.pii;

// ////////////////////////////////////////////////////////////////////////

pii.config = {

    lineId: 'mcp-wizard-pii-line',
    bodyId: 'mcp-wizard-pii-body',
    summaryId: 'mcp-wizard-summary-pii',

    labels: {
        masked: ' masked',
        removed: 'PII removed',
        kept: 'PII kept',
        joint: ', '
    }
};

// ////////////////////////////////////////////////////////////////////////

pii.summary = function() {

    var dataMasking = wizard.dataMasking;
    var labels = pii.config.labels;

    var maskedCount = dataMasking.maskedFields(dataMasking.state).length;
    var isRemovingPII = wizard.field('safeguards_pii_enabled').prop('checked');

    var out = dataMasking.countLabel(maskedCount) + labels.masked + labels.joint + (isRemovingPII ? labels.removed : labels.kept);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

pii._show = function(isOpen) {

    var config = pii.config;
    var chevronOpenClass = $.fn.zato.wizard_kit.collapse.config.chevronOpenClass;

    document.getElementById(config.bodyId).hidden = !isOpen;
    document.querySelector('#' + config.lineId + ' .wizard-chevron').classList.toggle(chevronOpenClass, isOpen);
};

// ////////////////////////////////////////////////////////////////////////

pii.init = function() {

    var config = pii.config;

    document.getElementById(config.lineId).addEventListener('click', function() {
        pii._show(document.getElementById(config.bodyId).hidden);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The review's edit link of the section - the step is already shown, the section opens on it.
pii.edit = function() {
    pii._show(true);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
