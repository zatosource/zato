$.fn.zato.envRepo = {};

// One button on the right. Connect with no address creates this dashboard's GitHub App and installs it, which is
// two pages on GitHub, then the repositories the App may read fill the address field. Connect with an address checks it
// with GitHub and lists the branches, and once they are listed, Connect again switches the environment over to the branch
// chosen. When GitHub refuses, the button reads Allow access and opens the App's page to add the repository on, or without
// an App, GitHub's deploy key page, then waits until GitHub lets us in.

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
    fadeDuration: 600,
    defaultBranch: 'main',
    deployKeyUrl: 'https://github.com/{owner}/{name}/settings/keys/new',
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
    appStateNone: 'none',
    appStateCreated: 'created',
    appStateInstalled: 'installed',
    addressKey: 'zato.envRepo.address',
};

$.fn.zato.envRepo.state = {
    mode: 'connect',
    appState: 'none',
    installUrl: '',
    requestTime: null,
    pollTimer: null,
    pollDeadline: null,
    retryTimer: null,
    branchTimer: null,
    keyDeadline: null,
    repo: null,
    isCreating: false,
    isConnected: false,
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

    state.isConnected = $('#disconnect-button').data('is-connected') === 1;
    state.appState = $('#repo-form').data('app-state');
    state.installUrl = $('#repo-form').data('install-url');
    $('#branch-placeholder').html($.fn.zato.empty_value);

    $('#create-button').on('click', $.fn.zato.envRepo.handleCreate);
    $('#disconnect-button').on('click', $.fn.zato.envRepo.handleDisconnect);
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

    $.fn.zato.envRepo.updateSide();

    // What GitHub's pages send the browser back with is read once and taken off the address bar.
    const params = new URLSearchParams(window.location.search);
    const isInstalledNow = params.get('installed') === '1';
    const error = params.get('error');

    if(params.has('installed') || params.has('error')) {
        window.history.replaceState(null, '', window.location.pathname);
    }

    if(error) {
        $.fn.zato.envRepo.showStatus(error, false);
    }

    // Back from GitHub with the App installed, the address typed before leaving is back in the field.
    if(isInstalledNow && !$('#repo-url').val().trim()) {
        $('#repo-url').val(window.sessionStorage.getItem(config.addressKey) || '');
        window.sessionStorage.removeItem(config.addressKey);
    }

    // A page that opens with an address already filled in connects on its own, unless the App has to be created
    // first, which is not started without a click, and one with an App installed but no address finds out which
    // repositories the App may read.
    if(state.appState !== config.appStateInstalled) {
        return;
    }

    if($('#repo-url').val().trim()) {
        $.fn.zato.envRepo.handleConnect();
    }
    else {
        $.fn.zato.envRepo.loadRepos(isInstalledNow);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The repositories the App may read go to the field's list, and one alone goes to the field itself. Right after the
// installation that one is connected without further ado, and several are left for the user to pick from.
$.fn.zato.envRepo.loadRepos = function(shouldConnect) {

    const list = $('#repo-list');

    $.fn.zato.envRepo.fetchRepos(function(repos) {

        list.empty();

        repos.forEach(function(fullName) {
            list.append($('<option></option>').attr('value', 'https://github.com/' + fullName));
        });

        if($('#repo-url').val().trim()) {
            return;
        }

        if(repos.length === 1) {
            $('#repo-url').val('https://github.com/' + repos[0]);
            $.fn.zato.envRepo.updateSide();

            if(shouldConnect) {
                $.fn.zato.envRepo.handleConnect();
            }
        }
        else if(shouldConnect) {
            $('#repo-url').focus();
        }

    }, function(errorMessage) {
        $.fn.zato.envRepo.showStatus(errorMessage, false);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The link on the left is what makes sense now - Create when there is no address, Disconnect when the address
// is the repository that runs now and its branches are listed, nothing otherwise.
$.fn.zato.envRepo.updateSide = function() {

    const state = $.fn.zato.envRepo.state;
    const address = $('#repo-url').val().trim();
    const currentUrl = $('#repo-url').data('current-url');
    const isCurrent = state.isConnected && state.mode === 'switch' && address === currentUrl;

    $('#create-button').toggleClass('hidden', address !== '');
    $('#disconnect-button').toggleClass('hidden', !isCurrent);
};

// ////////////////////////////////////////////////////////////////////////

// A repository just created has no key yet, so the next step is to allow access, not to connect.
$.fn.zato.envRepo.handleCreate = function() {

    $.fn.zato.envRepo.state.isCreating = true;
    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();
    $.fn.zato.envRepo.setMode('allow');

    $('#repo-url').val('');
    $.fn.zato.envRepo.updateSide();
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
    $.fn.zato.envRepo.updateSide();

    if(!$.fn.zato.envRepo.state.isCreating) {
        $.fn.zato.envRepo.setMode('connect');
    }
};

// ////////////////////////////////////////////////////////////////////////

// The mode is connect, switch or allow - the first two read Connect, the branch row is what tells them apart.
$.fn.zato.envRepo.setMode = function(mode) {

    const button = $('#action-button');
    const label = mode === 'allow' ? 'allow-label' : 'connect-label';

    $.fn.zato.envRepo.state.mode = mode;
    button.val(button.data(label));
    button.prop('disabled', false);

    $.fn.zato.envRepo.updateSide();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.resetFlow = function() {

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.setBranchView('branch-placeholder');
    $('#key-help').addClass('hidden');

    state.log.clear();
    state.log.hide();
    state.lastMessage = '';
    state.lineCount = 0;
};

// ////////////////////////////////////////////////////////////////////////

// The Branch cell shows one of the placeholder, the spinner or the list - what is on show fades out first,
// then what comes next fades in, and the row never changes its height.
$.fn.zato.envRepo.setBranchView = function(id) {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;
    const shown = $('#branch-cell > [data-shown="true"]');

    if(state.branchTimer) {
        clearTimeout(state.branchTimer);
        state.branchTimer = null;
    }

    if(shown.attr('id') === id) {
        return;
    }

    shown.attr('data-shown', 'false');

    state.branchTimer = setTimeout(function() {
        $('#' + id).attr('data-shown', 'true');
        state.branchTimer = null;
    }, shown.length ? config.fadeDuration : 0);
};

// ////////////////////////////////////////////////////////////////////////

// Starts the panel over for a new request, with the repository's name in its header.
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
        else if(status.state === 'ok' || status.state === 'switched' || status.state === 'disconnected') {
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

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;

    // No App yet - the App comes first, GitHub sends the browser back here once it is created, and if it is created
    // but not installed yet, its install page is where the browser goes. The address typed, if any, waits for the return.
    if(state.appState !== config.appStateInstalled) {

        window.sessionStorage.setItem(config.addressKey, $('#repo-url').val().trim());

        if(state.appState === config.appStateNone) {
            document.getElementById('github-app-form').submit();
        }
        else {
            window.location.href = state.installUrl;
        }

        return;
    }

    const address = $.fn.zato.envRepo.getValidAddress();

    if(address === null) {
        return;
    }

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();

    state.repo = $.fn.zato.envRepo.parseAddress(address);
    state.isQuiet = false;

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.setBranchView('branch-spinner');
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
    $.fn.zato.envRepo.setBranchView('branch-placeholder');

    $.fn.zato.envRepo.setMode('allow');
};

// ////////////////////////////////////////////////////////////////////////

// Connected - the branches take the spinner's place and Connect now means the switch to the one chosen.
$.fn.zato.envRepo.onConnected = function(status) {

    const state = $.fn.zato.envRepo.state;
    const branches = status.branches || [];

    state.isQuiet = false;
    state.isCreating = false;

    $.fn.zato.envRepo.stopAll();
    $('#key-help').addClass('hidden');

    $.fn.zato.envRepo.appendLine('Connected to ' + state.repo.full_name + ', ' + branches.length + ' ' + (branches.length === 1 ? 'branch' : 'branches'), 'ok');
    state.log.setState('done');

    $.fn.zato.envRepo.fillBranches(branches);
    $.fn.zato.envRepo.setBranchView('repo-branch');

    $.fn.zato.envRepo.setMode('switch');
};

// ////////////////////////////////////////////////////////////////////////

// Opens GitHub's page in a new tab for the repository to be added on - the App's installation page with an App,
// the deploy key page with the key to copy without one - and keeps checking until GitHub lets us in.
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

    const hasApp = state.appState === config.appStateInstalled;
    const url = hasApp ? state.installUrl : $.fn.zato.envRepo.getKeyUrl(state.repo);

    // The tab opens here, within the click, or the browser would block it.
    window.open(url, '_blank', 'noopener');

    $('#action-button').prop('disabled', true);

    if(hasApp) {
        $.fn.zato.envRepo.startLog(state.repo, 'Waiting for GitHub to allow access to ' + state.repo.full_name);
    }
    else {
        $.fn.zato.envRepo.startLog(state.repo, 'Waiting for GitHub to accept the key for ' + state.repo.full_name);

        if($('#public-key').text().trim()) {
            $('#deploy-key-link').attr('href', url);
            $('#key-help').removeClass('hidden');
        }
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
            $.fn.zato.envRepo.appendLine('GitHub has not allowed access to ' + state.repo.full_name, 'error');
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
    else if(status.state === 'switched' || status.state === 'disconnected') {
        state.log.setState('done');
        setTimeout(function() {
            window.location.reload();
        }, config.reloadDelay);
    }
    else {
        state.log.setState('failed');
        $.fn.zato.envRepo.setMode(state.mode);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Disconnects from the repository that runs now, a host goes back to the public blueprint.
$.fn.zato.envRepo.handleDisconnect = function(e) {

    e.preventDefault();

    const state = $.fn.zato.envRepo.state;
    const repo = $.fn.zato.envRepo.parseAddress($('#repo-url').data('current-url') || $('#repo-url').val().trim());

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();

    state.isQuiet = false;

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(repo, 'Disconnecting from ' + repo.full_name);

    $.fn.zato.envRepo.sendRequest('disconnect', function() {
        $.fn.zato.envRepo.pollStatus(['switching', 'disconnected'], $.fn.zato.envRepo.onSwitchDone);
    }, function(errorMessage) {
        $.fn.zato.envRepo.onSwitchDone({state: 'error', message: errorMessage, lines: []});
    });
};

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.envRepo.init();
});
