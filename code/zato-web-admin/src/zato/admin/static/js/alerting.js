// The alert rules listing - the glue around the shared ruleset browser. The per-rule
// actions post to the action endpoint and repaint the browser's panel in place, and
// creation opens a classic form popup asking for the rule's name before the editor opens.

$.fn.zato.alerting = {};

$.fn.zato.alerting.config = {
    actionUrl: '',
    editorUrl: '',
    clusterId: '',
    definitionId: 0,
    deletePrompt: 'Delete the rule {0}?',
    newNamePattern: /^[A-Za-z_]\w*$/,
    newNameHint: 'A rule name is letters, digits and underscores, starting with a letter'
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
    $('#alerting-create-div').dialog('open');
    document.getElementById('alerting-create-name').focus();
};

$.fn.zato.alerting.submitCreate = function() {

    var config = $.fn.zato.alerting.config;
    var name = document.getElementById('alerting-create-name').value.trim();

    if(!config.newNamePattern.test(name)) {
        jAlert(config.newNameHint, 'Invalid name');
        return;
    }

    window.location.href = config.editorUrl + '?cluster=' + config.clusterId + '&new=' + encodeURIComponent(name);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.init = function(config) {

    $.fn.zato.alerting.config.actionUrl = config.actionUrl;
    $.fn.zato.alerting.config.editorUrl = config.editorUrl;
    $.fn.zato.alerting.config.clusterId = config.clusterId;
    $.fn.zato.alerting.config.definitionId = config.definitionId;

    // The create popup - the same dialog every other listing creates through.
    var createDiv = $('#alerting-create-div');

    createDiv.dialog({
        autoOpen: false,
        width: '40em',
        title: 'Create a new alert rule',
        close: function() {
            document.getElementById('alerting-create-name').value = '';
        }
    });

    document.getElementById('alerting-create-form').addEventListener('submit', function(event) {
        event.preventDefault();
        $.fn.zato.alerting.submitCreate();
    });

    document.getElementById('alerting-create-cancel').addEventListener('click', function() {
        createDiv.dialog('close');
    });
};
