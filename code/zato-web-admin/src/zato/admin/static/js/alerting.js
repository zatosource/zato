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

// The browser's cached rules carry each rule's name - the confirmation reads it from there.
$.fn.zato.alerting.ruleName = function(ruleKey) {

    var config = $.fn.zato.alerting.config;
    var rules = rulesetsModel.cachedRules(config.definitionId);

    var match = rules.filter(function(rule) { return rule.key === ruleKey; })[0];
    var out = match.name;
    return out;
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
};

$.fn.zato.alerting.submitCreate = function() {

    var config = $.fn.zato.alerting.config;
    var form = $('#create-form');
    var field = $('#id_name');
    var name = field.val().trim();

    // An empty name blinks the field with the required message ..
    if(!$.fn.zato.is_form_valid(form)) {
        return;
    }

    // .. a name outside the engine's grammar reads its verdict in place,
    // the same way a taken one does ..
    if(!config.newNamePattern.test(name)) {
        $.fn.zato.render_unique_indicator(field, name, true, 'name', config.newNameMessage, config.newNameMessage);
        $.fn.zato.blink_elem(field);
        $.fn.zato.add_css_attention(field);
        field.focus();
        return;
    }

    // .. a taken name never leaves the popup ..
    if(!$.fn.zato.validate_unique_on_submit(form)) {
        return;
    }

    // .. and a good one opens the editor on a fresh rule of that name.
    window.location.href = config.editorUrl + '?cluster=' + config.clusterId + '&new=' + encodeURIComponent(name);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.init = function(config) {

    $.fn.zato.alerting.config.actionUrl = config.actionUrl;
    $.fn.zato.alerting.config.editorUrl = config.editorUrl;
    $.fn.zato.alerting.config.nameExistsUrl = config.nameExistsUrl;
    $.fn.zato.alerting.config.clusterId = config.clusterId;
    $.fn.zato.alerting.config.definitionId = config.definitionId;

    // The create popup - the same dialog every other listing creates through,
    // narrower because the one name field is all it holds.
    $('#create-div').dialog({
        autoOpen: false,
        width: '24em',
        close: function() {
            $.fn.zato.data_table.reset_form('#create-form');
        }
    });

    // The name is required and must be free - checked live while typing and again on OK,
    // against this screen's own store rather than the shared SQL-backed endpoint.
    $.fn.zato.data_table.set_field_required('#id_name');
    $.fn.zato.validate_unique('#id_name', 'alert_rule', 'name', null, null, config.nameExistsUrl);

    document.getElementById('create-form').addEventListener('submit', function(event) {
        event.preventDefault();
        $.fn.zato.alerting.submitCreate();
    });
};
