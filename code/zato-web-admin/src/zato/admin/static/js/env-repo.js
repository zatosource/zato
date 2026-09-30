$.fn.zato.envRepo = {};

// The page has one action button whose label follows the mode - connect checks the address with GitHub,
// allow opens GitHub's deploy key page with our key filled in and waits until GitHub accepts it,
// and switch changes the environment over to the branch chosen.

$.fn.zato.envRepo.config = {
    apiPrefix: '/zato/env-repo/',
    pollInterval: 1000,
    pollTimeout: 180000,
    keyRetryInterval: 5000,
    keyWaitTimeout: 900000,
    deployPollInterval: 2000,
    deployProgressPath: '/zato-deploy/progress.json',
    reloadDelay: 1500,
    statusFadeDelay: 2000,
    defaultBranch: 'main',
    deployKeyUrl: 'https://github.com/{owner}/{name}/settings/keys/new',
    deployKeyTitle: 'Zato',
    repoPatterns: [
        /^(?:https?:\/\/)?(?:www\.)?github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+?(?:\.git)?(?:[/?#].*)?$/,
        /^(?:ssh:\/\/)?git@github\.com[:/][A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+?(?:\.git)?\/?$/,
        /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+?(?:\.git)?$/,
    ],
    emptyAddressMessage: 'Enter the address of the repository',
    badAddressMessage: 'The address must look like https://github.com/owner/name',
    copiedMessage: 'Copied to clipboard',
    copiedShownDelay: 950,
    progressTheme: 'dark',
};

$.fn.zato.envRepo.state = {
    mode: 'connect',
    requestTime: null,
    pollTimer: null,
    pollDeadline: null,
    retryTimer: null,
    keyDeadline: null,
    repo: null,
    isCreating: false,
    isQuiet: false,
    lastMessage: '',
    lineCount: 0,
    log: null,
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.init = function() {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;

    state.log = progressLog.create({
        container: document.getElementById('progress-log'),
        theme: config.progressTheme,
        isHidden: true,
    });

    $('#create-button').on('click', $.fn.zato.envRepo.handleCreate);
    $('#copy-key').on('click', $.fn.zato.envRepo.handleCopyKey);
    $('#repo-url').on('input', $.fn.zato.envRepo.handleUrlInput);

    // The button and Enter submit the form, which is what lets the browser remember the addresses entered.
    $('#repo-form').on('submit', function(e) {
        e.preventDefault();
        $.fn.zato.envRepo.handleSubmit();
    });

    // Back from GitHub, the address of the new repository is what comes next.
    $(window).on('focus', function() {
        if(state.isCreating && !$('#repo-url').val().trim()) {
            $('#repo-url').focus();
        }
    });

    // A page that opens with an address already filled in connects on its own.
    if($('#repo-url').val().trim()) {
        $.fn.zato.envRepo.handleConnect();
    }
};

// ////////////////////////////////////////////////////////////////////////

// A repository just created has no key yet, so the next step is to allow access, not to connect.
$.fn.zato.envRepo.handleCreate = function() {

    $.fn.zato.envRepo.state.isCreating = true;
    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();
    $.fn.zato.envRepo.setMode('allow');

    $('#repo-url').val('');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleCopyKey = function() {

    const config = $.fn.zato.envRepo.config;
    const icon = this;
    const text = $('#public-key').text();

    navigator.clipboard.writeText(text).then(function() {

        // One element holds one tooltip at a time, and the one from a moment ago may still be on screen.
        if(icon._tippy) {
            icon._tippy.destroy();
        }

        const tooltip = tippy(icon, {
            content: config.copiedMessage,
            placement: 'top',
            trigger: 'manual',
            theme: 'dark',
            arrow: true,
        });

        tooltip.show();

        setTimeout(function() {
            tooltip.hide();
            setTimeout(function() {
                tooltip.destroy();
            }, 200);
        }, config.copiedShownDelay);
    });
};

// ////////////////////////////////////////////////////////////////////////

// A new address starts the flow over, unless the page is waiting for the address of a repository just created.
$.fn.zato.envRepo.handleUrlInput = function() {

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();
    $.fn.zato.envRepo.clearFieldError();

    if(!$.fn.zato.envRepo.state.isCreating) {
        $.fn.zato.envRepo.setMode('connect');
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.setMode = function(mode) {

    const button = $('#action-button');

    $.fn.zato.envRepo.state.mode = mode;
    button.val(button.data(mode + '-label'));
    button.prop('disabled', false);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.resetFlow = function() {

    const state = $.fn.zato.envRepo.state;

    $('#branch-row').addClass('hidden');
    $('#key-help').addClass('hidden');

    state.log.clear();
    state.log.hide();
    state.lastMessage = '';
    state.lineCount = 0;
};

// ////////////////////////////////////////////////////////////////////////

// Opens the panel for a new request, with the repository's name in its header.
$.fn.zato.envRepo.startLog = function(repo, message) {

    const state = $.fn.zato.envRepo.state;

    state.log.clear();
    state.log.setSource(repo.full_name);
    state.log.setState('live');
    state.log.show();
    state.lastMessage = '';
    state.lineCount = 0;

    $.fn.zato.envRepo.appendLine(message, null);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.appendLine = function(text, kind) {
    $.fn.zato.envRepo.state.log.append({text: text, kind: kind, time: new Date()});
};

// ////////////////////////////////////////////////////////////////////////

// Each status carries all the lines of its request so far, only the ones not shown yet go to the panel,
// and its message goes there once, when it changes.
$.fn.zato.envRepo.appendStatus = function(status) {

    const state = $.fn.zato.envRepo.state;

    if(state.isQuiet) {
        return;
    }

    const lines = status.lines || [];

    for(let idx = state.lineCount; idx < lines.length; idx++) {
        $.fn.zato.envRepo.appendLine(lines[idx], null);
    }

    state.lineCount = lines.length;

    if(status.message && status.message !== state.lastMessage) {

        let kind = null;

        if(status.state === 'error') {
            kind = 'error';
        }
        else if(status.state === 'ok' || status.state === 'switched') {
            kind = 'ok';
        }

        $.fn.zato.envRepo.appendLine(status.message, kind);
        state.lastMessage = status.message;
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

$.fn.zato.envRepo.handleSubmit = function() {

    const mode = $.fn.zato.envRepo.state.mode;

    if(mode === 'allow') {
        $.fn.zato.envRepo.handleAllow();
    }
    else if(mode === 'switch') {
        $.fn.zato.envRepo.handleSwitch();
    }
    else {
        $.fn.zato.envRepo.handleConnect();
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleConnect = function() {

    const state = $.fn.zato.envRepo.state;
    const address = $.fn.zato.envRepo.getValidAddress();

    if(address === null) {
        return;
    }

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();

    state.repo = $.fn.zato.envRepo.parseAddress(address);
    state.isQuiet = false;

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(state.repo, 'Connecting to ' + state.repo.full_name);

    $.fn.zato.envRepo.sendCheck(function(status) {
        if(status.state === 'ok') {
            $.fn.zato.envRepo.onConnected(status);
        }
        else {
            $.fn.zato.envRepo.onRefused(status);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.sendCheck = function(onDone) {

    $.fn.zato.envRepo.sendRequest('check', function() {
        $.fn.zato.envRepo.pollStatus(['ok'], onDone);
    }, function(errorMessage) {
        onDone({state: 'error', message: errorMessage, lines: []});
    });
};

// ////////////////////////////////////////////////////////////////////////

// GitHub refused the key, so the next step is to add it - the button says so and the panel shows why.
$.fn.zato.envRepo.onRefused = function(status) {

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.appendStatus(status);
    state.log.setState('failed');

    $.fn.zato.envRepo.setMode('allow');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onConnected = function(status) {

    const state = $.fn.zato.envRepo.state;
    const branches = status.branches || [];

    state.isQuiet = false;
    state.isCreating = false;

    $.fn.zato.envRepo.appendLine('Connected to ' + state.repo.full_name + ', ' + branches.length + ' ' + (branches.length === 1 ? 'branch' : 'branches'), 'ok');
    state.log.setState('done');

    $('#key-help').addClass('hidden');
    $.fn.zato.envRepo.fillBranches(branches);
    $('#branch-row').removeClass('hidden');

    $.fn.zato.envRepo.setMode('switch');
};

// ////////////////////////////////////////////////////////////////////////

// Opens GitHub's deploy key page in a new tab and keeps checking until the key lets us in.
$.fn.zato.envRepo.handleAllow = function() {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;
    const address = $.fn.zato.envRepo.getValidAddress();

    if(address === null) {
        return;
    }

    $.fn.zato.envRepo.stopAll();

    state.repo = $.fn.zato.envRepo.parseAddress(address);
    state.keyDeadline = Date.now() + config.keyWaitTimeout;

    // The tab opens here, within the click, or the browser would block it.
    window.open($.fn.zato.envRepo.getKeyUrl(state.repo), '_blank', 'noopener');

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(state.repo, 'Waiting for GitHub to accept the key for ' + state.repo.full_name);

    // The key is also on this page for anyone GitHub did not fill it in for.
    if($('#public-key').text().trim()) {
        $('#deploy-key-link').attr('href', $.fn.zato.envRepo.getKeyUrl(state.repo));
        $('#key-help').removeClass('hidden');
    }

    $.fn.zato.envRepo.retryCheck();
};

// ////////////////////////////////////////////////////////////////////////

// Each refusal while waiting is expected and stays out of the panel, only the outcome goes in.
$.fn.zato.envRepo.retryCheck = function() {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;

    state.isQuiet = true;

    $.fn.zato.envRepo.sendCheck(function(status) {

        if(status.state === 'ok') {
            $.fn.zato.envRepo.onConnected(status);
            return;
        }

        if(Date.now() > state.keyDeadline) {
            state.isQuiet = false;
            $.fn.zato.envRepo.appendLine('GitHub has not accepted the key', 'error');
            $.fn.zato.envRepo.appendStatus(status);
            state.log.setState('failed');
            $.fn.zato.envRepo.setMode('allow');
            return;
        }

        state.retryTimer = setTimeout($.fn.zato.envRepo.retryCheck, config.keyRetryInterval);
    });
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

    const state = $.fn.zato.envRepo.state;
    const branch = $('#repo-branch').val();

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.clearStatus();

    state.isQuiet = false;

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(state.repo, 'Switching to ' + state.repo.full_name + ' at ' + branch);

    $.fn.zato.envRepo.sendRequest('switch', function() {
        $.fn.zato.envRepo.pollStatus(['switching', 'switched'], $.fn.zato.envRepo.onSwitchDone);
    }, function(errorMessage) {
        $.fn.zato.envRepo.onSwitchDone({state: 'error', message: errorMessage, lines: []});
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onSwitchDone = function(status) {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.appendStatus(status);

    // A host restarts the environment after this state, without one the switch is already complete.
    if(status.state === 'switching') {
        $.fn.zato.envRepo.appendLine('The environment is restarting, the loading page opens once it is up', null);
        $.fn.zato.envRepo.waitForDeployPage();
    }
    else if(status.state === 'switched') {
        state.log.setState('done');
        setTimeout(function() {
            window.location.reload();
        }, config.reloadDelay);
    }
    else {
        state.log.setState('failed');
        $.fn.zato.envRepo.setMode('switch');
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

$.fn.zato.envRepo.stopAll = function() {

    const state = $.fn.zato.envRepo.state;

    if(state.pollTimer) {
        clearTimeout(state.pollTimer);
        state.pollTimer = null;
    }

    if(state.retryTimer) {
        clearTimeout(state.retryTimer);
        state.retryTimer = null;
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.pollStatus = function(finalStates, onDone) {

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

            if(isFresh) {
                $.fn.zato.envRepo.appendStatus(status);
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
