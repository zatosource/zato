// The alert rules listing - toggling a rule's active flag happens where it is read,
// deletion and publishing confirm first, and creating a rule asks for its name
// in a prompt before the editor opens on it.

$.fn.zato.alerting = {};

$.fn.zato.alerting.config = {
    actionUrl: '',
    editorUrl: '',
    clusterId: '',
    prompts: {
        'delete': 'Delete the rule {0}?',
        publish: 'Publish the current draft so it goes live?'
    },
    newNamePattern: /^[A-Za-z_]\w*$/,
    newNameHint: 'A rule name is letters, digits and underscores, starting with a letter'
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.post = function(data) {

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

            // The listing reflects the new state once it reloads.
            window.location.reload();
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

$.fn.zato.alerting.run = function(action, ruleKey, ruleName) {

    var config = $.fn.zato.alerting.config;

    var data = {
        action: action
    };

    // Publishing acts on the whole ruleset, everything else on one rule.
    if(action !== 'publish') {
        data.rule = ruleKey;
    }

    // Toggling the active flag happens right away, the rest confirms first.
    if(action === 'activate' || action === 'deactivate') {
        $.fn.zato.alerting.post(data);
        return;
    }

    var question = config.prompts[action].replace('{0}', ruleName);

    jConfirm(question, 'Please confirm', function(confirmed) {
        if(confirmed) {
            $.fn.zato.alerting.post(data);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.createRule = function() {

    var config = $.fn.zato.alerting.config;

    jPrompt('Name of the new rule', '', 'Create a new alert rule', function(name) {

        // A dismissed prompt means nothing to create.
        if(name === null) {
            return;
        }

        name = name.trim();

        if(!config.newNamePattern.test(name)) {
            jAlert(config.newNameHint, 'Invalid name');
            return;
        }

        window.location.href = config.editorUrl + '?cluster=' + config.clusterId + '&new=' + encodeURIComponent(name);
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.alerting.init = function(config) {

    $.fn.zato.alerting.config.actionUrl = config.actionUrl;
    $.fn.zato.alerting.config.editorUrl = config.editorUrl;
    $.fn.zato.alerting.config.clusterId = config.clusterId;

    // One delegated listener covers every action link in every tab's table.
    var card = document.querySelector('.alerting-card');

    card.addEventListener('click', function(event) {

        var target = event.target.closest('[data-rule-action]');

        if(!target) {
            return;
        }

        event.preventDefault();

        $.fn.zato.alerting.run(
            target.getAttribute('data-rule-action'),
            target.getAttribute('data-rule'),
            target.getAttribute('data-rule-name')
        );
    });

    var newLink = document.getElementById('alerting-new-link');
    newLink.addEventListener('click', $.fn.zato.alerting.createRule);

    // The publish link is only on the page when there is a draft to publish.
    var publishLink = document.getElementById('alerting-publish-link');

    if(publishLink) {
        publishLink.addEventListener('click', function() {
            $.fn.zato.alerting.run('publish', null, null);
        });
    }
};
