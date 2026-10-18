// MCP gateway wizard - the PII row of step 2.
//
// One row saying what the PII detection runs on. A click on its link opens
// a popover under the step strip holding all the PII fields at once. The
// fields are moved into the popover and back to their holder on the step
// once it closes, so the form keeps its inputs and the multi-selects their state.
// The fields edit the form directly, which is why OK only closes the popover.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var forms = wizard.forms;
var pii = wizard.pii;

// ////////////////////////////////////////////////////////////////////////

pii.config = {

    descriptorName: 'pii',
    kindName: 'piiFields',
    title: 'PII',
    width: 640,

    // The popover opens centered over the card and this far under its step strip
    openTop: 12,
    viewportMargin: 24,

    cardId: 'mcp-wizard',
    stepsId: 'mcp-wizard-steps',
    editLinkId: 'mcp-wizard-edit-pii',
    holderId: 'mcp-wizard-pii-holder',
    bodyId: 'mcp-wizard-pii-body',
    summaryId: 'mcp-wizard-summary-pii',

    labels: {
        off: 'Off',
        nothingPicked: 'No lands or detectors picked',
        lands: 'Lands: ',
        detectors: 'Detectors: ',
        separator: ', '
    }
};

// ////////////////////////////////////////////////////////////////////////

// The texts of the options picked in one of the PII multi-selects.
pii._picked = function(fieldName) {

    var out = [];

    wizard.field(fieldName).find('option:selected').each(function() {
        out.push(this.textContent);
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Off, or what the detection runs on - the detectors picked by name take
// precedence over the lands, the way the gateway applies them.
pii.summary = function() {

    var labels = pii.config.labels;

    if(!wizard.field('safeguards_pii_enabled').prop('checked')) {
        return labels.off;
    }

    var detectors = pii._picked('safeguards_pii_detectors');
    var lands = pii._picked('safeguards_pii_lands');

    var out;

    if(detectors.length) {
        out = labels.detectors + detectors.join(labels.separator);
    }
    else if(lands.length) {
        out = labels.lands + lands.join(labels.separator);
    }
    else {
        out = labels.nothingPicked;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

pii._openAt = function() {

    var config = pii.config;
    var card = document.getElementById(config.cardId).getBoundingClientRect();
    var steps = document.getElementById(config.stepsId).getBoundingClientRect();

    var centeredLeft = card.left + (card.width - config.width) / 2;

    var out = {
        left: Math.max(config.viewportMargin, centeredLeft),
        top: steps.bottom + config.openTop
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

pii.open = function() {
    forms.open(pii.config.descriptorName, document.getElementById(pii.config.editLinkId));
};

// ////////////////////////////////////////////////////////////////////////

pii._build = function(fieldSpec, row) {

    row.classList.add('micro-form-field-own');
    row.appendChild(document.getElementById(pii.config.bodyId));
};

// ////////////////////////////////////////////////////////////////////////

// The fields return to their holder on the step, and the row says what they now hold.
pii._putAway = function() {

    var config = pii.config;

    document.getElementById(config.holderId).appendChild(document.getElementById(config.bodyId));
    wizard.review.setSummary(config.summaryId, pii.summary());
};

// ////////////////////////////////////////////////////////////////////////

pii.init = function() {
    $('#' + pii.config.editLinkId).on('click', pii.open);
};

// ////////////////////////////////////////////////////////////////////////

// The review's edit link of the section - the step is already shown, the popover opens on it.
pii.edit = function() {
    pii.open();
};

// ////////////////////////////////////////////////////////////////////////

forms.registerKind(pii.config.kindName, {
    build: pii._build,
    save: function() {}
});

forms.descriptors[pii.config.descriptorName] = {
    title: pii.config.title,
    width: pii.config.width + 'px',
    floating: true,
    openAt: pii._openAt,
    pages: [[{kind: pii.config.kindName}]],
    onClose: pii._putAway
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
