// MCP gateway wizard - live summaries, the option cards and the review step.
//
// Every line and card on step 2 carries a one-line summary of what is
// currently configured, recomputed from the form each time a micro-form
// closes or an inline field changes. The review step renders the same data
// as grouped rows through the wizard kit's renderer, each group with an
// Edit link that jumps back to the step the answers came from.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var review = wizard.review;

$.fn.zato.wizard_kit.review.setup(wizard);

// ////////////////////////////////////////////////////////////////////////

review.config = {

    // What the review says about a pick not made yet
    noneLabel: 'None',

    // The words the shaping summaries are written with
    noCapLabel: 'No cap',
    tokensMaxLabel: ' tokens max, ',
    fromLabel: ', from ',
    allowedLabel: 'Allowed',
    notAllowedLabel: 'Not allowed',

    // The words the option summaries are written with
    onLabel: 'On',
    offLabel: 'Off',
    yesLabel: 'Yes',
    noLabel: 'No',
    ofLabel: ' of ',
    validationOnLabel: 'Validation on',
    validationOffLabel: 'Validation off',
    auditLogOnLabel: 'audit log on',
    auditLogOffLabel: 'audit log off',
    compactionLabel: ' compaction',
    piiOnLabel: 'PII on',
    piiOffLabel: 'PII off',
    safetyChecksLabel: ' safety checks',
    nothingSelectedLabel: 'On, nothing selected yet',
    landsLabel: ' lands',
    landLabel: ' land',
    detectorsLabel: ' detectors',
    detectorLabel: ' detector',
    hostsAllowedLabel: ' hosts allowed',
    hostAllowedLabel: ' host allowed',
    allUrlsLabel: 'all URLs checked',

    // The compaction toggles, in the order the popover shows them
    compactionFields: [
        'safeguards_strip_nulls',
        'safeguards_collapse_whitespace',
        'safeguards_strip_base64'
    ],

    // What each compaction toggle is called on the review
    compactionLabels: {
        safeguards_strip_nulls: 'Strip null fields',
        safeguards_collapse_whitespace: 'Collapse whitespace',
        safeguards_strip_base64: 'Strip base64 blobs'
    },

    // The content safety master toggles, counted for the summaries
    safetyFields: [
        'safeguards_normalize_unicode',
        'safeguards_sanitize_markup',
        'safeguards_url_policy_enabled'
    ],

    // The words the picker card summaries are written with
    assignedLabel: ' assigned',
    noneAssignedLabel: 'None assigned'
};

// ////////////////////////////////////////////////////////////////////////

// The three badge picker cards of step 1 - each folds its picker away the
// way the PII and content safety cards of step 2 fold their fields.
review.pickerCards = function() {

    var ownConfig = wizard.config_own;

    var out = [
        {name: 'services', action: ownConfig.pickerAction},
        {name: 'skills',   action: ownConfig.skillsPickerAction},
        {name: 'security', action: ownConfig.securityPickerAction}
    ];

    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.initOptionCards = function() {

    // The picker cards of step 1 expand and collapse in place, and each
    // summary follows its assigned zone as badges move in and out ..
    review.pickerCards().forEach(function(card) {

        $('#mcp-wizard-' + card.name + '-header').on('click', function() {
            $('#mcp-wizard-' + card.name + '-body').toggleClass('wizard-option-body-open');
            $('#mcp-wizard-' + card.name + '-chevron').toggleClass('wizard-chevron-open');
        });

        // The pickers load after this wiring runs and badges travel between
        // the zones with plain DOM moves, so the assigned zone's child list
        // is what the summary follows
        var assignedZone = document.querySelector('#badge-zone-assigned-' + card.action + ' .badge-zone-body');

        var observer = new MutationObserver(function() {
            review.setSummary('mcp-wizard-summary-' + card.name, review._pickerSummary(card.action));
        });

        observer.observe(assignedZone, {childList: true});
    });

    // .. the two smaller cards open their micro-forms ..
    $('#mcp-wizard-card-gateway-options').on('click', function() {
        wizard.forms.open('gateway_options', this);
    });

    $('#mcp-wizard-card-compaction').on('click', function() {
        wizard.forms.open('compaction', this);
    });

    // .. the PII and content safety cards expand and collapse in place ..
    $('#mcp-wizard-pii-header').on('click', function() {
        $('#mcp-wizard-pii-body').toggleClass('wizard-option-body-open');
        $('#mcp-wizard-pii-chevron').toggleClass('wizard-chevron-open');
    });

    $('#mcp-wizard-safety-header').on('click', function() {
        $('#mcp-wizard-safety-body').toggleClass('wizard-option-body-open');
        $('#mcp-wizard-safety-chevron').toggleClass('wizard-chevron-open');
    });

    // .. each content safety group opens and closes on its own ..
    $.fn.zato.wizard_kit.collapse.initGroups('#mcp-wizard-safety-body');

    review._placeFieldGridHelp();

    // .. the whole options block is folded away behind one line,
    // its link saying what is inside ..
    $.fn.zato.wizard_kit.collapse.initSection({
        toggleId: 'mcp-wizard-edit-options',
        bodyId: 'mcp-wizard-options-body',
        hintId: 'mcp-wizard-hint-options'
    });

    // .. and the summaries follow the inline fields as they change - the
    // micro-forms refresh them on their own when they close.
    $('#mcp-wizard-step-body-1 input[type="checkbox"], #mcp-wizard-step-body-1 select').on('change', function() {
        review.refreshSummaries();
    });
};

// ////////////////////////////////////////////////////////////////////////

// A grid row is a label with its control at the end of it, so a tooltip
// anchored on the control would sit right on top of the label it explains.
// Anchoring on the label and sending the tooltip past its left edge keeps
// the whole row visible - the card's own left margin is where it goes.
review._placeFieldGridHelp = function() {

    $('.mcp-wizard-field-grid label[for], .mcp-wizard-pii-selects label[for]').each(function() {
        $(this).attr('data-help-anchor', 'label');
        $(this).attr('data-help-placement', 'left');
    });
};

// ////////////////////////////////////////////////////////////////////////

review._sizeCapsSummary = function() {

    var config = review.config;

    var maxSize = wizard.field('max_response_size').val().trim();
    if(!maxSize) {
        return config.noCapLabel;
    }

    var mode = wizard.field('size_cap_mode').find('option:selected').text().toLowerCase();
    var out = maxSize + config.tokensMaxLabel + mode;

    var threshold = wizard.field('min_size_threshold').val().trim();
    if(threshold) {
        out += config.fromLabel + threshold;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._gatewayOptionsSummary = function() {

    var config = review.config;
    var parts = [];

    parts.push(wizard.field('validate_input').prop('checked') ? config.validationOnLabel : config.validationOffLabel);
    parts.push(wizard.field('is_audit_log_active').prop('checked') ? config.auditLogOnLabel : config.auditLogOffLabel);

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How many of the given toggles are on.
review._checkedCount = function(fieldList) {

    var out = 0;

    for(var fieldIdx = 0; fieldIdx < fieldList.length; fieldIdx++) {
        if(wizard.field(fieldList[fieldIdx]).prop('checked')) {
            out++;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._compactionSummary = function() {

    var config = review.config;

    var out = review._checkedCount(config.compactionFields) + config.ofLabel + config.compactionFields.length + ' on';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What one PII multi-select holds - the labels of its picked options.
review._multiSelectLabels = function(fieldName) {

    var out = [];

    wizard.field(fieldName).find('option:selected').each(function() {
        out.push(this.textContent);
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._piiSummary = function() {

    var config = review.config;

    if(!wizard.field('safeguards_pii_enabled').prop('checked')) {
        return config.offLabel;
    }

    var landCount = review._multiSelectLabels('safeguards_pii_lands').length;
    var detectorCount = review._multiSelectLabels('safeguards_pii_detectors').length;

    if(!landCount && !detectorCount) {
        return config.nothingSelectedLabel;
    }

    var parts = [];

    if(landCount) {
        parts.push(landCount + (landCount === 1 ? config.landLabel : config.landsLabel));
    }

    if(detectorCount) {
        parts.push(detectorCount + (detectorCount === 1 ? config.detectorLabel : config.detectorsLabel));
    }

    var out = config.onLabel + ', ' + parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What one picker card's summary says - how many badges its assigned
// zone holds.
review._pickerSummary = function(pickerAction) {

    var config = review.config;

    var assignedCount = wizard.assignedBadges(pickerAction).length;
    if(!assignedCount) {
        return config.noneAssignedLabel;
    }

    var out = assignedCount + config.assignedLabel;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._safetySummary = function() {

    var config = review.config;

    var out = review._checkedCount(config.safetyFields) + config.ofLabel + config.safetyFields.length + ' on';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the one line above the folded options says - the shape of each of
// the four, counted rather than listed.
review._optionsSummary = function() {

    var config = review.config;
    var parts = [];

    parts.push(wizard.field('validate_input').prop('checked') ? config.validationOnLabel : config.validationOffLabel);
    parts.push(wizard.field('is_audit_log_active').prop('checked') ? config.auditLogOnLabel : config.auditLogOffLabel);
    parts.push(review._checkedCount(config.compactionFields) + config.ofLabel +
        config.compactionFields.length + config.compactionLabel);
    parts.push(wizard.field('safeguards_pii_enabled').prop('checked') ? config.piiOnLabel : config.piiOffLabel);
    parts.push(review._checkedCount(config.safetyFields) + config.ofLabel +
        config.safetyFields.length + config.safetyChecksLabel);

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Recomputes every line and card summary.
review.refreshSummaries = function() {

    review.pickerCards().forEach(function(card) {
        review.setSummary('mcp-wizard-summary-' + card.name, review._pickerSummary(card.action));
    });

    review.setSummary('mcp-wizard-summary-size-caps', review._sizeCapsSummary());
    review.setSummary('mcp-wizard-summary-options', review._optionsSummary());
    review.setSummary('mcp-wizard-summary-gateway-options', review._gatewayOptionsSummary());
    review.setSummary('mcp-wizard-summary-compaction', review._compactionSummary());
    review.setSummary('mcp-wizard-summary-pii', review._piiSummary());
    review.setSummary('mcp-wizard-summary-safety', review._safetySummary());
};

// ////////////////////////////////////////////////////////////////////////

// The badges assigned in one picker, each as one [key, value] review row.
review._badgeListRows = function(pickerAction, rowKey) {

    var out = [];

    wizard.assignedBadges(pickerAction).each(function() {

        var badge = $(this);
        var name = badge.find('.security-badge-name').text();

        // A security badge says its type in front of its name, a service
        // badge carries the name alone
        var typeName = badge.find('.security-badge-type').text();

        out.push([typeName ? typeName : rowKey, name]);
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The PII rows for the review - the switch alone while it is off, the whole
// of the selection once it is on.
review._piiReviewRows = function() {

    var config = review.config;

    if(!wizard.field('safeguards_pii_enabled').prop('checked')) {
        return [['Enabled', config.noLabel]];
    }

    var landLabels = review._multiSelectLabels('safeguards_pii_lands');
    var detectorLabels = review._multiSelectLabels('safeguards_pii_detectors');
    var excludeLabels = review._multiSelectLabels('safeguards_pii_exclude');

    var out = [
        ['Enabled', config.yesLabel],
        ['Lands', landLabels.length ? landLabels.join(', ') : config.noneLabel],
        ['Detectors', detectorLabels.length ? detectorLabels.join(', ') : config.noneLabel],
        ['Exclude', excludeLabels.length ? excludeLabels.join(', ') : config.noneLabel],
        ['Validate checksums', wizard.field('safeguards_pii_validate').prop('checked') ? config.onLabel : config.offLabel],
        ['Stable replacements', wizard.field('safeguards_pii_stable_replacements').prop('checked') ? config.onLabel : config.offLabel]
    ];

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One content safety check as the review reads it - Off, or the answer its
// mode select gives to what happens when something is found.
review._safetyModeSummary = function(toggleName, modeName) {

    var config = review.config;

    if(!wizard.field(toggleName).prop('checked')) {
        return config.offLabel;
    }

    var out = wizard.field(modeName).find('option:selected').text();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._urlPolicySummary = function() {

    var config = review.config;

    if(!wizard.field('safeguards_url_policy_enabled').prop('checked')) {
        return config.offLabel;
    }

    var mode = wizard.field('safeguards_url_mode').find('option:selected').text();

    var allowList = wizard.field('safeguards_url_allow_list').val().trim();
    if(!allowList) {
        return mode + ', ' + config.allUrlsLabel;
    }

    // The hosts travel comma-separated, so their count is what the review says
    var hostCount = 0;
    var hostList = allowList.split(',');

    for(var hostIdx = 0; hostIdx < hostList.length; hostIdx++) {
        if(hostList[hostIdx].trim()) {
            hostCount++;
        }
    }

    var out = mode + ', ' + hostCount + (hostCount === 1 ? config.hostAllowedLabel : config.hostsAllowedLabel);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What a group's Edit link opens once the step it belongs to is on screen,
// so the answer is there to be changed rather than to be looked for. The
// Basics group has none - its answers are the top rows of step 1 itself.

// A picker card inside a closed body has nothing to show, so an Edit link
// opens the card first and reveals it then.
review._openPickerCard = function(name) {

    if(!$('#mcp-wizard-' + name + '-body').hasClass('wizard-option-body-open')) {
        $('#mcp-wizard-' + name + '-header').trigger('click');
    }

    wizard.reveal(document.getElementById('mcp-wizard-picker-' + name));
};

// ////////////////////////////////////////////////////////////////////////

review._editServices = function() {
    review._openPickerCard('services');
};

// ////////////////////////////////////////////////////////////////////////

review._editSkills = function() {
    review._openPickerCard('skills');
};

// ////////////////////////////////////////////////////////////////////////

review._editSecurity = function() {
    review._openPickerCard('security');
};

// ////////////////////////////////////////////////////////////////////////

review._editSizeCaps = function() {
    wizard.forms.open('size_caps', document.getElementById('mcp-wizard-edit-size-caps'));
};

// ////////////////////////////////////////////////////////////////////////

// The four option cards are folded away behind the More options line, so
// that line goes first - a card inside a closed body has nothing to open on.
review._openOptions = function() {

    if($('#mcp-wizard-options-body').prop('hidden')) {
        $('#mcp-wizard-edit-options').trigger('click');
    }
};

// ////////////////////////////////////////////////////////////////////////

review._editGatewayOptions = function() {

    review._openOptions();
    wizard.forms.open('gateway_options', document.getElementById('mcp-wizard-card-gateway-options'));
};

// ////////////////////////////////////////////////////////////////////////

review._editCompaction = function() {

    review._openOptions();
    wizard.forms.open('compaction', document.getElementById('mcp-wizard-card-compaction'));
};

// ////////////////////////////////////////////////////////////////////////

review._editPII = function() {

    review._openOptions();

    if(!$('#mcp-wizard-pii-body').hasClass('wizard-option-body-open')) {
        $('#mcp-wizard-pii-header').trigger('click');
    }
};

// ////////////////////////////////////////////////////////////////////////

review._editSafety = function() {

    review._openOptions();

    if(!$('#mcp-wizard-safety-body').hasClass('wizard-option-body-open')) {
        $('#mcp-wizard-safety-header').trigger('click');
    }
};

// ////////////////////////////////////////////////////////////////////////

// Renders the review step from the current form state.
review.render = function() {

    var config = review.config;
    var ownConfig = wizard.config_own;
    var groups = ownConfig.groups;

    // Basics
    var basicsRows = [
        ['Name', wizard.field('name').val().trim()],
        ['Active', wizard.field('is_active').prop('checked') ? config.yesLabel : config.noLabel],
        ['URL path', wizard.field('url_path').val().trim()]
    ];

    // Services and security - each pick is a row of its own, so a long list
    // scrolls, and a picker left empty says so in a row the reader can check
    var serviceListRows = review._badgeListRows(ownConfig.pickerAction, 'Service');
    var serviceRows = [];

    if(!serviceListRows.length) {
        serviceRows.push(['Assigned', config.noneLabel]);
    }

    var skillListRows = review._badgeListRows(ownConfig.skillsPickerAction, 'Skill');
    var skillRows = [];

    if(!skillListRows.length) {
        skillRows.push(['Assigned', config.noneLabel]);
    }

    var securityListRows = review._badgeListRows(ownConfig.securityPickerAction, 'Definition');
    var securityRows = [];

    if(!securityListRows.length) {
        securityRows.push(['Assigned', config.noneLabel]);
    }

    // Response shaping
    var shapingRows = [
        ['Allow client filters', wizard.field('allow_client_filters').prop('checked') ? config.allowedLabel : config.notAllowedLabel],
        ['Size cap', review._sizeCapsSummary()],
        ['Characters per token', wizard.field('characters_per_token').val().trim()]
    ];

    // Gateway options
    var gatewayOptionsRows = [
        ['Validate input', wizard.field('validate_input').prop('checked') ? config.onLabel : config.offLabel],
        ['Audit log', wizard.field('is_audit_log_active').prop('checked') ? config.onLabel : config.offLabel]
    ];

    // Compaction
    var compactionRows = [];

    for(var fieldIdx = 0; fieldIdx < config.compactionFields.length; fieldIdx++) {
        var fieldName = config.compactionFields[fieldIdx];
        var isChecked = wizard.field(fieldName).prop('checked');
        compactionRows.push([config.compactionLabels[fieldName], isChecked ? config.onLabel : config.offLabel]);
    }

    // Content safety
    var safetyRows = [
        ['Unicode', review._safetyModeSummary('safeguards_normalize_unicode', 'safeguards_unicode_mode')],
        ['Markup', review._safetyModeSummary('safeguards_sanitize_markup', 'safeguards_markup_mode')],
        ['URL policy', review._urlPolicySummary()]
    ];

    review.renderGroups([
        {label: groups.basics,         step: 0, rows: basicsRows},
        {label: groups.services,       step: 0, listRows: serviceListRows, rows: serviceRows,
            edit: review._editServices},
        {label: groups.skills,         step: 0, listRows: skillListRows, rows: skillRows,
            edit: review._editSkills},
        {label: groups.security,       step: 0, listRows: securityListRows, rows: securityRows,
            edit: review._editSecurity},
        {label: groups.shaping,        step: 1, rows: shapingRows, edit: review._editSizeCaps},
        {label: groups.gatewayOptions, step: 1, rows: gatewayOptionsRows, edit: review._editGatewayOptions},
        {label: groups.compaction,     step: 1, rows: compactionRows, edit: review._editCompaction},
        {label: groups.pii,            step: 1, rows: review._piiReviewRows(), edit: review._editPII},
        {label: groups.contentSafety,  step: 1, rows: safetyRows, edit: review._editSafety}
    ]);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
