// The alert rules listing - the glue around the shared ruleset browser. The per-rule
// actions post to the action endpoint and repaint the browser's panel in place, and
// creation opens a classic form popup asking for the rule's name before the editor opens.

$.fn.zato.alerting = {};

$.fn.zato.alerting.config = {
    actionUrl: '',
    editorUrl: '',
    nameExistsUrl: '',
    clusterId: '',
    definitionId: 0,
    deletePrompt: 'Delete the rule {0}?',

    // The rule engine's own name grammar - a name becomes a token of the stored document
    newNamePattern: /^\w+$/,
    newNameMessage: 'Letters, digits and underscores only'
};

// What the how-it-works walkthrough says about each field, the create
// and the edit popup alike.
$.fn.zato.alerting.field_descriptions = {
    'id_name': 'A unique name for this rule.<br>Letters, digits and underscores only,<br>shown across the monitoring screens.',
    'id_docs': 'What this rule is for, in your own words.<br>Shown next to the rule in the listing.',
    'id_edit-name': 'A unique name for this rule.<br>Letters, digits and underscores only,<br>shown across the monitoring screens.',
    'id_edit-docs': 'What this rule is for, in your own words.<br>Shown next to the rule in the listing.',
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.post = function(data, onDone) {

    var config = $.fn.zato.alerting.config;

    $.ajax({
        url: config.actionUrl,
        type: 'POST',
        data: data,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(response) {

            if(typeof response === 'string') {
                response = JSON.parse(response);
            }

            // An action that could not run answers with an error inside a 200.
            if(response.error) {
                jAlert(response.error, 'Error');
                return;
            }

            onDone();
        },
        error: function(request) {

            var text = request.responseText;

            try {
                var payload = JSON.parse(text);
                if(payload.error) {
                    text = payload.error;
                }
            }
            catch(ignored) {
            }

            jAlert(text, 'Error');
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// The browser's cached rules carry each rule's name and docs - the confirmation
// and the edit popup both read from there.
$.fn.zato.alerting.rule = function(ruleKey) {

    var config = $.fn.zato.alerting.config;
    var rules = rulesetsModel.cachedRules(config.definitionId);

    var out = rules.filter(function(rule) { return rule.key === ruleKey; })[0];
    return out;
};

$.fn.zato.alerting.ruleName = function(ruleKey) {
    return $.fn.zato.alerting.rule(ruleKey).name;
};

// After a change went through, the browser refetches the set and repaints in place.
$.fn.zato.alerting.refresh = function() {
    rulesetsView.refreshRules($.fn.zato.alerting.config.definitionId);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.runAction = function(action, ruleKey) {
    $.fn.zato.alerting.post({action: action, rule: ruleKey}, $.fn.zato.alerting.refresh);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.deleteRule = function(ruleKey) {

    var config = $.fn.zato.alerting.config;
    var question = config.deletePrompt.replace('{0}', $.fn.zato.alerting.ruleName(ruleKey));

    jConfirm(question, 'Please confirm', function(confirmed) {

        if(!confirmed) {
            return;
        }

        $.fn.zato.alerting.post({action: 'delete', rule: ruleKey}, $.fn.zato.alerting.refresh);
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.openCreate = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new monitoring rule', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.alerting.field_descriptions
    });
};

// A name outside the engine's grammar reads its verdict in place,
// the same way a taken one does.
$.fn.zato.alerting.nameIsValid = function(field) {

    var config = $.fn.zato.alerting.config;
    var name = field.val().trim();

    if(config.newNamePattern.test(name)) {
        return true;
    }

    $.fn.zato.render_unique_indicator(field, name, true, 'name', config.newNameMessage, config.newNameMessage);
    $.fn.zato.blink_elem(field);
    $.fn.zato.add_css_attention(field);
    field.focus();
    return false;
};

$.fn.zato.alerting.submitCreate = function() {

    var config = $.fn.zato.alerting.config;
    var form = $('#create-form');
    var field = $('#id_name');
    var name = field.val().trim();
    var docs = $('#id_docs').val().trim();

    // An empty name blinks the field with the required message ..
    if(!$.fn.zato.is_form_valid(form)) {
        return;
    }

    // .. a name outside the engine's grammar never leaves the popup ..
    if(!$.fn.zato.alerting.nameIsValid(field)) {
        return;
    }

    // .. a taken one does not either ..
    if(!$.fn.zato.validate_unique_on_submit(form)) {
        return;
    }

    // .. and a good one opens the editor on a fresh rule of that name,
    // carrying the description along.
    window.location.href = config.editorUrl + '?cluster=' + config.clusterId +
        '&new=' + encodeURIComponent(name) + '&docs=' + encodeURIComponent(docs);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.openEdit = function(ruleKey) {

    var rule = $.fn.zato.alerting.rule(ruleKey);

    // The popup opens prefilled from the browser's cache - no population from
    // the data_table machinery, this screen has no data_table rows.
    $.fn.zato.data_table._create_edit('edit', 'Edit a monitoring rule', null, undefined, false);

    var nameField = $('#id_edit-name');
    nameField.val(rule.name);

    // The name as it is now - the uniqueness machinery skips the check while
    // the field still holds it, so a rule can keep its own name.
    nameField.data('zato-original-value', rule.name);

    $('#id_edit-docs').val(rule.docs);

    // Which rule the OK button acts on.
    $('#edit-form').data('zato-rule-key', ruleKey);

    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.alerting.field_descriptions
    });
};

$.fn.zato.alerting.submitEdit = function() {

    var form = $('#edit-form');
    var field = $('#id_edit-name');
    var name = field.val().trim();
    var docs = $('#id_edit-docs').val().trim();
    var ruleKey = form.data('zato-rule-key');

    // An empty name blinks the field with the required message ..
    if(!$.fn.zato.is_form_valid(form)) {
        return;
    }

    // .. a name outside the engine's grammar never leaves the popup ..
    if(!$.fn.zato.alerting.nameIsValid(field)) {
        return;
    }

    // .. a name another rule already holds does not either - the check skips
    // a name this rule keeps unchanged ..
    if(!$.fn.zato.validate_unique_on_submit(form)) {
        return;
    }

    // .. and a good one is stored, the popup closes and the panel repaints.
    $.fn.zato.alerting.post({action: 'update', rule: ruleKey, name: name, docs: docs}, function() {
        $('#edit-div').dialog('close');
        $.fn.zato.alerting.refresh();
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.init = function(config) {

    $.fn.zato.alerting.config.actionUrl = config.actionUrl;
    $.fn.zato.alerting.config.editorUrl = config.editorUrl;
    $.fn.zato.alerting.config.nameExistsUrl = config.nameExistsUrl;
    $.fn.zato.alerting.config.clusterId = config.clusterId;
    $.fn.zato.alerting.config.definitionId = config.definitionId;

    // The create and edit popups - the same dialogs every other listing goes through,
    // narrower because a name and a description are all they hold.
    $('#create-div').dialog({
        autoOpen: false,
        width: '24em',
        close: function() {
            $.fn.zato.data_table.reset_form('#create-form');
        }
    });

    $('#edit-div').dialog({
        autoOpen: false,
        width: '24em',
        close: function() {
            $.fn.zato.data_table.reset_form('#edit-form');
        }
    });

    // The name is required and must be free - checked live while typing and again on OK,
    // against this screen's own store rather than the shared SQL-backed endpoint. The edit
    // popup's check skips a name the rule keeps unchanged.
    $.fn.zato.data_table.set_field_required('#id_name');
    $.fn.zato.validate_unique('#id_name', 'alert_rule', 'name', null, null, config.nameExistsUrl);

    $.fn.zato.data_table.set_field_required('#id_edit-name');
    $.fn.zato.validate_unique('#id_edit-name', 'alert_rule', 'name', null, null, config.nameExistsUrl);

    document.getElementById('create-form').addEventListener('submit', function(event) {
        event.preventDefault();
        $.fn.zato.alerting.submitCreate();
    });

    document.getElementById('edit-form').addEventListener('submit', function(event) {
        event.preventDefault();
        $.fn.zato.alerting.submitEdit();
    });
};
