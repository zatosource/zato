$.fn.zato.envRepo = {};

$.fn.zato.envRepo.config = {
    apiPrefix: '/zato/env-repo/',
    pollInterval: 1000,
    pollTimeout: 180000,
    deployPollInterval: 2000,
    deployProgressPath: '/zato-deploy/progress.json',
    reloadDelay: 1500,
    statusFadeDelay: 2000,
    defaultBranch: 'main',
    spinnerPath: '/static/gfx/spinner.svg',
    repoPatterns: [
        /^(?:https?:\/\/)?(?:www\.)?github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+?(?:\.git)?(?:[/?#].*)?$/,
        /^(?:ssh:\/\/)?git@github\.com[:/][A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+?(?:\.git)?\/?$/,
        /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+?(?:\.git)?$/,
    ],
    emptyAddressMessage: 'Enter the address of the repository',
    badAddressMessage: 'The address must look like https://github.com/owner/name',
    copiedMessage: 'Copied',
};

$.fn.zato.envRepo.state = {
    requestTime: null,
    pollTimer: null,
    pollDeadline: null,
    repo: null,
    isCreating: false,
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.init = function() {

    $('#create-button').on('click', $.fn.zato.envRepo.handleCreate);
    $('#check-button').on('click', $.fn.zato.envRepo.handleConnect);
    $('#update-button').on('click', $.fn.zato.envRepo.handleSwitch);
    $('#copy-key').on('click', $.fn.zato.envRepo.handleCopyKey);

    $('#repo-url').on('input', $.fn.zato.envRepo.handleUrlInput);
    $('#repo-url').on('keydown', function(e) {
        if(e.key === 'Enter') {
            e.preventDefault();
            $.fn.zato.envRepo.handleConnect();
        }
    });

    // Back from GitHub, the address of the new repository is what comes next.
    $(window).on('focus', function() {
        if($.fn.zato.envRepo.state.isCreating && !$('#repo-url').val().trim()) {
            $('#repo-url').focus();
        }
    });

    // A page that opens with an address already filled in connects on its own.
    if($('#repo-url').val().trim()) {
        $.fn.zato.envRepo.handleConnect();
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleCreate = function() {
    $.fn.zato.envRepo.state.isCreating = true;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleCopyKey = function() {

    const icon = $(this);
    const text = $('#public-key').text();

    navigator.clipboard.writeText(text).then(function() {
        $.fn.zato.envRepo.showStatus($.fn.zato.envRepo.config.copiedMessage, true);
        icon.css('opacity', 1);
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleUrlInput = function() {

    // A new address starts the flow over.
    $.fn.zato.envRepo.stopPolling();
    $.fn.zato.envRepo.resetFlow();
    $.fn.zato.envRepo.clearFieldError();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.showStatus = function(message, isOK) {

    const config = $.fn.zato.envRepo.config;
    const status = $('#env-repo-status');

    status.removeClass('show fade status-message-success status-message-error');
    status.text(message).addClass('show ' + (isOK ? 'status-message-success' : 'status-message-error'));

    if(isOK) {
        setTimeout(function() {
            status.addClass('fade');
            setTimeout(function() {
                status.removeClass('show fade status-message-success');
            }, 500);
        }, config.statusFadeDelay);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.clearStatus = function() {
    $('#env-repo-status').removeClass('show fade status-message-success status-message-error').text('');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.showFieldError = function(message) {

    $('#repo-url').addClass('env-repo-error').focus();
    $.fn.zato.envRepo.showStatus(message, false);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.clearFieldError = function() {

    $('#repo-url').removeClass('env-repo-error');
    $.fn.zato.envRepo.clearStatus();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.isAddressValid = function(address) {

    const patterns = $.fn.zato.envRepo.config.repoPatterns;

    for(let idx = 0; idx < patterns.length; idx++) {
        if(patterns[idx].test(address)) {
            return true;
        }
    }

    return false;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.resetFlow = function() {

    $('#branch-row').addClass('hidden');
    $('#update-button').addClass('hidden').prop('disabled', false);
    $('#check-button').prop('disabled', false);
    $('#key-help').addClass('hidden');
    $('#step-check, #step-switch').addClass('hidden').removeClass('error completed');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.renderStep = function(step, state, message, lines) {

    const config = $.fn.zato.envRepo.config;
    const item = $('#step-' + step);
    const icon = item.find('.env-repo-step-icon');
    const linesElem = item.find('.env-repo-step-lines');

    item.removeClass('hidden error completed');
    item.find('.env-repo-step-message').text(message);

    if(state === 'processing') {
        icon.html('<img src="' + config.spinnerPath + '">');
    }
    else if(state === 'completed') {
        item.addClass('completed');
        icon.text('\u2713');
    }
    else {
        item.addClass('error');
        icon.text('\u2717');
    }

    if(lines && lines.length) {
        linesElem.text(lines.join('\n')).removeClass('hidden');
    }
    else {
        linesElem.text('').addClass('hidden');
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.getInput = function() {

    const out = {
        url: $('#repo-url').val().trim(),
        branch: $('#repo-branch').val() || '',
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleConnect = function() {

    const config = $.fn.zato.envRepo.config;
    const address = $('#repo-url').val().trim();

    $.fn.zato.envRepo.stopPolling();
    $.fn.zato.envRepo.resetFlow();
    $.fn.zato.envRepo.clearFieldError();

    // The address is checked here first, nothing is sent until it has the right shape.
    if(!address) {
        $.fn.zato.envRepo.showFieldError(config.emptyAddressMessage);
        return;
    }

    if(!$.fn.zato.envRepo.isAddressValid(address)) {
        $.fn.zato.envRepo.showFieldError(config.badAddressMessage);
        return;
    }

    $('#check-button').prop('disabled', true);
    $.fn.zato.envRepo.renderStep('check', 'processing', 'Connecting to GitHub...');

    $.fn.zato.envRepo.sendRequest('check', function(response) {
        $.fn.zato.envRepo.state.repo = response;
        $.fn.zato.envRepo.renderStep('check', 'processing', 'Connecting to ' + response.full_name + '...');
        $.fn.zato.envRepo.pollStatus('check', ['ok'], $.fn.zato.envRepo.onConnectDone);
    }, function(errorMessage) {
        $('#check-button').prop('disabled', false);
        $('#step-check').addClass('hidden');
        $.fn.zato.envRepo.showFieldError(errorMessage);
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onConnectDone = function(status) {

    const repo = $.fn.zato.envRepo.state.repo;

    $('#check-button').prop('disabled', false);

    if(status.state === 'ok') {
        $.fn.zato.envRepo.renderStep('check', 'completed', 'Connected to ' + repo.full_name);
        $.fn.zato.envRepo.fillBranches(status.branches || []);
        $('#branch-row').removeClass('hidden');
        $('#update-button').removeClass('hidden');
    }
    else {
        $.fn.zato.envRepo.renderStep('check', 'error', status.message, status.lines);
        $('#deploy-key-link').attr('href', repo.deploy_key_url);
        $('#key-help').removeClass('hidden');
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.fillBranches = function(branches) {

    const select = $('#repo-branch');
    select.empty();

    branches.forEach(function(branch) {
        select.append($('<option></option>').attr('value', branch).text(branch));
    });

    // The branch that runs now comes first, then main, then whatever is first.
    const currentBranch = $('#repo-url').data('current-branch');
    const defaultBranch = $.fn.zato.envRepo.config.defaultBranch;

    let selected = branches[0];

    if(branches.indexOf(currentBranch) !== -1) {
        selected = currentBranch;
    }
    else if(branches.indexOf(defaultBranch) !== -1) {
        selected = defaultBranch;
    }

    select.val(selected);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleSwitch = function() {

    const button = $(this);
    button.prop('disabled', true);

    $.fn.zato.envRepo.stopPolling();
    $.fn.zato.envRepo.clearStatus();
    $.fn.zato.envRepo.renderStep('switch', 'processing', 'Switching the repository...');

    $.fn.zato.envRepo.sendRequest('switch', function() {
        $.fn.zato.envRepo.pollStatus('switch', ['switching', 'switched'], function(status) {
            $.fn.zato.envRepo.onSwitchDone(status, button);
        });
    }, function(errorMessage) {
        button.prop('disabled', false);
        $.fn.zato.envRepo.renderStep('switch', 'error', errorMessage);
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onSwitchDone = function(status, button) {

    // A host restarts the environment after this state, without one the switch is already complete.
    if(status.state === 'switching') {
        $.fn.zato.envRepo.renderStep('switch', 'processing', 'The environment is restarting, the loading page opens once it is up...');
        $.fn.zato.envRepo.waitForDeployPage();
    }
    else if(status.state === 'switched') {
        $.fn.zato.envRepo.renderStep('switch', 'completed', status.message);
        setTimeout(function() {
            window.location.reload();
        }, $.fn.zato.envRepo.config.reloadDelay);
    }
    else {
        button.prop('disabled', false);
        $.fn.zato.envRepo.renderStep('switch', 'error', status.message, status.lines);
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
        success: function(response) {
            onSuccess(response);
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
        $.fn.zato.envRepo.fetchStatus(function(status) {

            // Only a status written after the request went out is an answer to it ..
            const isFresh = status && new Date(status.time) >= state.requestTime;

            if(isFresh && (finalStates.indexOf(status.state) !== -1 || status.state === 'error')) {
                state.pollTimer = null;
                onDone(status);
                return;
            }

            if(isFresh && status.message) {
                $.fn.zato.envRepo.renderStep(step, 'processing', status.message);
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

$.fn.zato.envRepo.fetchStatus = function(onStatus) {

    $.ajax({
        url: $.fn.zato.envRepo.config.apiPrefix + 'status',
        type: 'GET',
        success: function(response) {
            onStatus(response.status);
        },
        error: function() {
            onStatus(null);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.envRepo.init();
});
