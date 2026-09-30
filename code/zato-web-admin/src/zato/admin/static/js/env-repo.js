$.fn.zato.envRepo = {};

$.fn.zato.envRepo.config = {
    apiPrefix: '/zato/env-repo/',
    pollInterval: 1000,
    pollTimeout: 180000,
    deployPollInterval: 2000,
    deployProgressPath: '/zato-deploy/progress.json',
};

$.fn.zato.envRepo.state = {
    requestTime: null,
    pollTimer: null,
    pollDeadline: null,
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.init = function() {

    $('#check-button').on('click', $.fn.zato.envRepo.handleCheck);
    $('#update-button').on('click', $.fn.zato.envRepo.handleSwitch);
    $('.copy-icon').on('click', $.fn.zato.settings.handleCopyIcon);
    $('#github-login').on('input', $.fn.zato.envRepo.handleLoginInput);

    $('#create-repo-link, #add-key-link').on('click', $.fn.zato.envRepo.handleLinkClick);

    $.fn.zato.envRepo.updateLinks();
    $.fn.zato.envRepo.fetchStatus(false);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleLoginInput = function() {
    $.fn.zato.envRepo.updateLinks();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleLinkClick = function(e) {

    // The links lead nowhere until there is a login to build them from.
    if($(this).attr('href') === '#') {
        e.preventDefault();
        $('#github-login').focus();
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.updateLinks = function() {

    const login = $('#github-login').val().trim();
    const createLink = $('#create-repo-link');
    const addKeyLink = $('#add-key-link');

    if(!login) {
        createLink.attr('href', '#').addClass('env-repo-link-disabled');
        addKeyLink.attr('href', '#').addClass('env-repo-link-disabled');
        return;
    }

    $.ajax({
        url: $.fn.zato.envRepo.config.apiPrefix + 'links',
        type: 'GET',
        data: {login: login},
        success: function(response) {
            createLink.attr('href', response.new_repo_url).removeClass('env-repo-link-disabled');
            addKeyLink.attr('href', response.deploy_key_url).removeClass('env-repo-link-disabled');

            // The address of the new repository is what the user will switch to.
            const repoUrl = $('#repo-url');
            if(!repoUrl.data('edited')) {
                repoUrl.val(response.repo_ssh_url);
            }
        },
        error: function() {
            createLink.attr('href', '#').addClass('env-repo-link-disabled');
            addKeyLink.attr('href', '#').addClass('env-repo-link-disabled');
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.getInput = function() {

    const out = {
        url: $('#repo-url').val().trim(),
        branch: $('#repo-branch').val().trim(),
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleCheck = function() {

    $.fn.zato.envRepo.stopPolling();
    $.fn.zato.settings.activateSpinner('.button-spinner');

    $('#progress-switch').addClass('hidden').removeClass('error-state');
    $('#progress-check').removeClass('hidden error-state');
    $.fn.zato.settings.updateProgress('check', 'processing', 'Connecting to GitHub...');

    $.fn.zato.envRepo.sendRequest('check', function() {
        $.fn.zato.envRepo.pollStatus('check', ['ok'], $.fn.zato.envRepo.onCheckDone);
    }, function(errorMessage) {
        $.fn.zato.settings.deactivateSpinner('.button-spinner');
        $.fn.zato.settings.updateProgress('check', 'error', errorMessage);
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onCheckDone = function(status) {

    $.fn.zato.settings.deactivateSpinner('.button-spinner');

    if(status.state === 'ok') {
        $.fn.zato.settings.updateProgress('check', 'completed', status.message);
        $.fn.zato.envRepo.flashOK();
    }
    else {
        $('#progress-check').data('full-error', status.message + '\n\n' + status.lines.join('\n'));
        $.fn.zato.settings.updateProgress('check', 'error', status.message);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.flashOK = function() {

    const message = $('.status-message');
    message.addClass('show');

    setTimeout(function() {
        message.addClass('fade');
        setTimeout(function() {
            message.removeClass('show fade');
        }, 500);
    }, 1500);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleSwitch = function() {

    const button = $(this);
    button.prop('disabled', true);

    $.fn.zato.envRepo.stopPolling();

    $('#progress-check').addClass('hidden').removeClass('error-state');
    $('#progress-switch').removeClass('hidden error-state');
    $.fn.zato.settings.updateProgress('switch', 'processing', 'Switching the repository...');

    $.fn.zato.envRepo.sendRequest('switch', function() {
        $.fn.zato.envRepo.pollStatus('switch', ['switching', 'switched'], function(status) {
            $.fn.zato.envRepo.onSwitchDone(status, button);
        });
    }, function(errorMessage) {
        button.prop('disabled', false);
        $.fn.zato.settings.updateProgress('switch', 'error', errorMessage);
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onSwitchDone = function(status, button) {

    // A host restarts the environment after this state, without one the switch is already complete.
    if(status.state === 'switching') {
        $.fn.zato.settings.updateProgress('switch', 'processing', 'The host is restarting the environment, the loading page opens once it is up...');
        $.fn.zato.envRepo.waitForDeployPage();
    }
    else if(status.state === 'switched') {
        button.prop('disabled', false);
        $.fn.zato.settings.updateProgress('switch', 'completed', status.message);
    }
    else {
        button.prop('disabled', false);
        $('#progress-switch').data('full-error', status.message + '\n\n' + status.lines.join('\n'));
        $.fn.zato.settings.updateProgress('switch', 'error', status.message);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.waitForDeployPage = function() {

    const config = $.fn.zato.envRepo.config;

    // Once the loading page answers on this port, the container is gone and the page takes over.
    const check = function() {
        fetch(config.deployProgressPath, {cache: 'no-store'}).then(function(response) {
            if(response.ok) {
                window.location.replace('/');
            }
            else {
                setTimeout(check, config.deployPollInterval);
            }
        }).catch(function() {
            setTimeout(check, config.deployPollInterval);
        });
    };

    setTimeout(check, config.deployPollInterval);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.sendRequest = function(action, onSuccess, onError) {

    const input = $.fn.zato.envRepo.getInput();
    $.fn.zato.envRepo.state.requestTime = new Date();

    $.ajax({
        url: $.fn.zato.envRepo.config.apiPrefix + action,
        type: 'POST',
        data: input,
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        success: function() {
            onSuccess();
        },
        error: function(xhr) {
            let errorMessage = 'Request could not be sent';
            try {
                const response = JSON.parse(xhr.responseText);
                errorMessage = response.error || errorMessage;
            } catch(e) {
            }
            onError(errorMessage);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.stopPolling = function() {

    const state = $.fn.zato.envRepo.state;

    if(state.pollTimer) {
        clearTimeout(state.pollTimer);
        state.pollTimer = null;
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.pollStatus = function(step, finalStates, onDone) {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;

    state.pollDeadline = Date.now() + config.pollTimeout;

    const poll = function() {
        $.fn.zato.envRepo.fetchStatus(true, function(status) {

            // Only a status written after the request went out is an answer to it ..
            const isFresh = status && new Date(status.time) >= state.requestTime;

            if(isFresh && (finalStates.indexOf(status.state) !== -1 || status.state === 'error')) {
                state.pollTimer = null;
                onDone(status);
                return;
            }

            if(isFresh && status.message) {
                $.fn.zato.settings.updateProgress(step, 'processing', status.message);
            }

            // .. and there is only so long to wait for one.
            if(Date.now() > state.pollDeadline) {
                state.pollTimer = null;
                onDone({state: 'error', message: 'No answer in time', lines: []});
                return;
            }

            state.pollTimer = setTimeout(poll, config.pollInterval);
        });
    };

    poll();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.fetchStatus = function(isPolling, onStatus) {

    $.ajax({
        url: $.fn.zato.envRepo.config.apiPrefix + 'status',
        type: 'GET',
        success: function(response) {
            $.fn.zato.envRepo.renderCurrent(response.current);
            $.fn.zato.envRepo.renderLog(response.status);
            if(onStatus) {
                onStatus(response.status);
            }
        },
        error: function() {
            if(onStatus) {
                onStatus(null);
            }
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.renderCurrent = function(current) {

    if(!current) {
        return;
    }

    $('#current-url').text(current.url).attr('title', current.url);
    $('#current-branch').text(current.branch);
    $('#current-commit').text(current.commit.substring(0, 12));
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.renderLog = function(status) {

    const container = $('#env-repo-log');
    container.empty();

    if(!status) {
        container.append($('<div class="env-repo-log-empty">No results</div>'));
        return;
    }

    const header = $('<div class="env-repo-log-header"></div>');
    header.append($('<span class="env-repo-log-time"></span>').text(new Date(status.time).toLocaleString()));
    header.append($('<span class="env-repo-log-state"></span>').addClass(status.state).text(status.state));
    container.append(header);

    container.append($('<div class="env-repo-log-message"></div>').text(status.message));

    if(status.lines.length) {
        const lines = $('<pre class="env-repo-log-lines"></pre>');
        lines.text(status.lines.join('\n'));
        container.append(lines);
    }
};

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#repo-url').on('input', function() {
        $(this).data('edited', true);
    });
    $.fn.zato.envRepo.init();
});
