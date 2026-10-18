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

    // What a picker card's summary says while nothing is assigned in it
    noneAssignedLabel: 'None assigned',

    // The one group the Skills card counts its badges in
    skillsLabel: 'Skills',

    // How each group of a picker card's summary is written, e.g. Services (3)
    countOpen: ' (',
    countClose: ')',
    groupSeparator: ', '
};

// ////////////////////////////////////////////////////////////////////////

// The three badge picker cards of step 1, each folding its picker away.
review.pickerCards = function() {

    var ownConfig = wizard.config_own;

    var out = [
        {name: 'tools',    action: ownConfig.pickerAction},
        {name: 'skills',   action: ownConfig.skillsPickerAction},
        {name: 'security', action: ownConfig.securityPickerAction}
    ];

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What one picker card has assigned, counted in groups - per tool source
// for the Tools card, per security type for the Security card and as one
// group for the Skills card. A group with nothing assigned is left out.
review._cardGroups = function(card) {

    var config = review.config;

    if(card.name === 'tools') {
        wizard.toolSources.syncCounts();
        return wizard.toolSources.assignedCounts();
    }

    var badges = wizard.assignedBadges(card.action);

    if(card.name === 'skills') {
        if(badges.length === 0) {
            return [];
        }
        return [{label: config.skillsLabel, count: badges.length}];
    }

    var out = [];
    var byType = {};

    // The types are counted in the order the assigned zone lists them
    badges.each(function() {

        var typeName = $(this).find('.security-badge-type').text();

        if(!(typeName in byType)) {
            byType[typeName] = {label: typeName, count: 0};
            out.push(byType[typeName]);
        }

        byType[typeName].count++;
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether the card is the Security one with OAuth sign-in active
review._isOAuthOn = function(card) {

    var out = card.name === 'security' && wizard.field('oauth').prop('checked');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How many things a card holds - its assigned badges, and OAuth sign-in on the Security card as one more.
review._cardCount = function(card) {

    var out = 0;

    review._cardGroups(card).forEach(function(group) {
        out += group.count;
    });

    if(review._isOAuthOn(card)) {
        out++;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What one picker card's summary says, e.g. Services (3), Microsoft Teams (1),
// or Bearer token (1), OAuth sign-in (2 scopes).
review._cardSummary = function(card) {

    var config = review.config;

    var parts = review._cardGroups(card).map(function(group) {
        return group.label + config.countOpen + group.count + config.countClose;
    });

    if(review._isOAuthOn(card)) {
        parts.push(wizard.assign.oauthSummary());
    }

    if(parts.length === 0) {
        return config.noneAssignedLabel;
    }

    var out = parts.join(config.groupSeparator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._showCardSummary = function(card) {
    review.setSummary('mcp-wizard-summary-' + card.name, review._cardSummary(card));
};

// ////////////////////////////////////////////////////////////////////////

review.initOptionCards = function() {

    // The picker cards of step 1 open their sections in the popover of assign.js, and each
    // summary, on the card and in the popover's index, follows its assigned zone
    // as badges move in and out ..
    review.pickerCards().forEach(function(card) {

        $('#mcp-wizard-' + card.name + '-header').on('click', function() {
            wizard.assign.open(card.name, this);
        });

        // The pickers load after this wiring runs and badges travel between
        // the zones with plain DOM moves, so the assigned zone's child list
        // is what the summary follows
        var assignedZone = document.querySelector('#badge-zone-assigned-' + card.action + ' .badge-zone-body');

        var observer = new MutationObserver(function() {
            review._showCardSummary(card);
            wizard.assign.refreshIndex();
        });

        observer.observe(assignedZone, {childList: true});
    });

    // .. the Security card's summary follows the OAuth switch and its scopes as well ..
    wizard.field('oauth').add(wizard.field('oauth_scopes')).on('change', function() {
        review.pickerCards().forEach(review._showCardSummary);
        wizard.assign.refreshIndex();
    });

    // .. the two smaller cards open their micro-forms ..
    $('#mcp-wizard-card-gateway-options').on('click', function() {
        wizard.forms.open('gateway_options', this);
    });

    $('#mcp-wizard-card-compaction').on('click', function() {
        wizard.forms.open('compaction', this);
    });

    review._placeFieldGridHelp();

    // .. the whole options block is folded away behind one line, the whole
    // of which opens and closes it, its link saying what is inside ..
    $.fn.zato.wizard_kit.collapse.initSection({
        toggleId: 'mcp-wizard-row-options',
        bodyId: 'mcp-wizard-options-body',
        hintId: 'mcp-wizard-hint-options',
        onToggle: function(isOpen) {
            $('#mcp-wizard-options-chevron').toggleClass('wizard-chevron-open', isOpen);
        }
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

    $('.mcp-wizard-field-grid label[for], .mcp-wizard-pii-fields label[for]').each(function() {
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

// What the one line above the folded options says - the shape of each of
// the cards, counted rather than listed.
review._optionsSummary = function() {

    var config = review.config;
    var parts = [];

    parts.push(wizard.field('validate_input').prop('checked') ? config.validationOnLabel : config.validationOffLabel);
    parts.push(wizard.field('is_audit_log_active').prop('checked') ? config.auditLogOnLabel : config.auditLogOffLabel);
    parts.push(review._checkedCount(config.compactionFields) + config.ofLabel +
        config.compactionFields.length + config.compactionLabel);

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Recomputes every line and card summary.
review.refreshSummaries = function() {

    review.pickerCards().forEach(review._showCardSummary);

    review.setSummary('mcp-wizard-summary-size-caps', review._sizeCapsSummary());
    review.setSummary(wizard.alerts.config.summaryId, wizard.alerts.summary());
    review.setSummary('mcp-wizard-summary-options', review._optionsSummary());
    review.setSummary('mcp-wizard-summary-gateway-options', review._gatewayOptionsSummary());
    review.setSummary('mcp-wizard-summary-compaction', review._compactionSummary());
    review.setSummary('mcp-wizard-summary-hooks', wizard.hooks.summary());
    wizard.dataMasking.refreshSummaries();
    review.setSummary(wizard.pii.config.summaryId, wizard.pii.summary());
    review.setSummary(wizard.contentSafety.config.summaryId, wizard.contentSafety.summary());
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
// of the selection once it is on, with the masked fields ahead of them either way.
review._piiReviewRows = function() {

    var config = review.config;

    var out;

    if(wizard.field('safeguards_pii_enabled').prop('checked')) {

        var landLabels = review._multiSelectLabels('safeguards_pii_lands');
        var detectorLabels = review._multiSelectLabels('safeguards_pii_detectors');
        var excludeLabels = review._multiSelectLabels('safeguards_pii_exclude');

        out = [
            ['Enabled', config.yesLabel],
            ['Lands', landLabels.length ? landLabels.join(', ') : config.noneLabel],
            ['Detectors', detectorLabels.length ? detectorLabels.join(', ') : config.noneLabel],
            ['Exclude', excludeLabels.length ? excludeLabels.join(', ') : config.noneLabel],
            ['Validate checksums', wizard.field('safeguards_pii_validate').prop('checked') ? config.onLabel : config.offLabel],
            ['Stable replacements', wizard.field('safeguards_pii_stable_replacements').prop('checked') ? config.onLabel : config.offLabel]
        ];
    }
    else {
        out = [['Enabled', config.noLabel]];
    }

    out.unshift(['Data masking', wizard.dataMasking.reviewValue()]);

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

// A picker card's Edit link opens the popover on the card's section.
review._openPickerCard = function(name) {
    wizard.assign.open(name, document.getElementById('mcp-wizard-' + name + '-header'));
};

// ////////////////////////////////////////////////////////////////////////

review._editTools = function() {
    review._openPickerCard('tools');
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

review._editAlerts = function() {
    wizard.alerts.open(document.getElementById(wizard.alerts.config.editLinkId));
};

// ////////////////////////////////////////////////////////////////////////

// The option cards are folded away behind the More options line, so
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

    // Tools and security - each pick is a row of its own, so a long list
    // scrolls, and a picker left empty says so in a row the reader can check.
    // A tool pick's row is keyed by the source it came from.
    var toolPicks = wizard.toolSources.allAssigned();
    var toolListRows = [];

    for(var pickIndex = 0; pickIndex < toolPicks.length; pickIndex++) {
        var pick = toolPicks[pickIndex];
        toolListRows.push([pick.label, pick.name]);
    }

    var toolRows = [];

    if(!toolListRows.length) {
        toolRows.push(['Assigned', config.noneLabel]);
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

    // OAuth with the customer's identity provider, with the scopes clients ask for while it is on
    var isOAuthOn = wizard.field('oauth').prop('checked');
    securityRows.push(['OAuth', isOAuthOn ? config.onLabel : config.offLabel]);

    if(isOAuthOn) {
        var oauthScopes = wizard.field('oauth_scopes').val().trim();
        securityRows.push(['Scopes', oauthScopes ? oauthScopes : config.noneLabel]);
    }

    // Response shaping
    var shapingRows = [
        ['Allow agent filters', wizard.field('allow_agent_filters').prop('checked') ? config.allowedLabel : config.notAllowedLabel],
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
        ['Secrets', wizard.field('safeguards_secrets_enabled').prop('checked') ? config.onLabel : config.offLabel],
        ['Unicode', review._safetyModeSummary('safeguards_normalize_unicode', 'safeguards_unicode_mode')],
        ['Markup', review._safetyModeSummary('safeguards_sanitize_markup', 'safeguards_markup_mode')],
        ['URL policy', review._urlPolicySummary()]
    ];

    review.renderGroups([
        {label: groups.basics,         step: 0, rows: basicsRows},
        {label: groups.tools,          step: 0, listRows: toolListRows, rows: toolRows,
            edit: review._editTools},
        {label: groups.skills,         step: 0, listRows: skillListRows, rows: skillRows,
            edit: review._editSkills},
        {label: groups.security,       step: 0, listRows: securityListRows, rows: securityRows,
            edit: review._editSecurity},
        {label: groups.shaping,        step: 1, rows: shapingRows, edit: review._editSizeCaps},
        {label: groups.alerts,         step: 1, rows: wizard.alerts.reviewRows(), edit: review._editAlerts},
        {label: groups.pii,            step: 1, rows: review._piiReviewRows(), edit: wizard.pii.edit},
        {label: groups.hooks,          step: 1, rows: wizard.hooks.reviewRows(), edit: wizard.hooks.edit},
        {label: groups.contentSafety,  step: 1, rows: safetyRows, edit: wizard.contentSafety.edit},
        {label: groups.gatewayOptions, step: 1, rows: gatewayOptionsRows, edit: review._editGatewayOptions},
        {label: groups.compaction,     step: 1, rows: compactionRows, edit: review._editCompaction}
    ]);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
