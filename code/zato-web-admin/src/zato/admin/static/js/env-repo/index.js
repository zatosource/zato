$.fn.zato.envRepo = {};

// One button on the right. Connect with no App yet creates this dashboard's GitHub App and installs it, which is
// two pages on GitHub, then the repositories the App may read fill the address field. Connect with an address checks it
// with GitHub and lists the branches, and once they are listed, the button reads Pull with Push next to it - Pull of the
// repository and branch that run now is a plain pull, Pull of any other switches the environment over to it first.
// When GitHub refuses, the button reads Allow access and opens the App's page to add the repository on, or without
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
    creatingKey: 'zato.envRepo.creating',
    hintPlacement: 'right',
    hintTheme: 'dark',
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
    isConnected: false,
    isChecked: false,
    isHost: false,
    hint: null,
    knownRepos: null,
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
    state.isChecked = $('#repo-form').data('is-checked') === 1;
    state.isHost = $('#repo-form').data('is-host') === 1;
    state.mode = $('#repo-form').data('mode');

    $('#disconnect-button').on('click', $.fn.zato.envRepo.handleDisconnect);
    $('#push-button').on('click', $.fn.zato.envRepo.handlePush);
    $('#repo-branch').on('change', $.fn.zato.envRepo.handleBranchChange);
    $('#copy-key').on('click', $.fn.zato.envRepo.handleCopyKey);
    $('#repo-url').on('input', $.fn.zato.envRepo.handleUrlInput);

    // The button and Enter submit the form, which is what lets the browser remember the addresses entered.
    $('#repo-form').on('submit', function(e) {
        e.preventDefault();
        $.fn.zato.envRepo.handleSubmit();
    });

    $.fn.zato.envRepo.initHint();
    $.fn.zato.envRepo.updateSide();

    // Back from GitHub with a repository just created, the App knows about it already.
    $(window).on('focus', $.fn.zato.envRepo.handleFocus);

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
    if(isInstalledNow) {
        const address = window.sessionStorage.getItem(config.addressKey) || '';
        window.sessionStorage.removeItem(config.addressKey);

        if(address) {
            $('#repo-url').val(address);
        }
    }

    // A page that opens with an address already filled in connects on its own, unless the App has to be created
    // first, which is not started without a click, and one with an App installed but no address finds out which
    // repositories the App may read.
    // The page came with the address checked already, its panel shows how that went.
    $.fn.zato.envRepo.showInitialStatus();

    if(state.appState !== config.appStateInstalled) {
        return;
    }

    if(!$('#repo-url').val().trim()) {
        $.fn.zato.envRepo.pickRepo(isInstalledNow);
    }
};

// ////////////////////////////////////////////////////////////////////////

// What the server found out about the address before the page was served goes into the panel as it is,
// nothing is asked of GitHub again.
$.fn.zato.envRepo.showInitialStatus = function() {

    const state = $.fn.zato.envRepo.state;
    const text = $('#progress-log').attr('data-status');

    if(!text) {
        return;
    }

    const status = JSON.parse(text);
    const address = $('#repo-url').val().trim();

    state.repo = $.fn.zato.envRepo.parseAddress(address);
    state.log.setSource(state.repo.full_name);

    $.fn.zato.envRepo.appendStatus(status);

    if(status.state === 'ok') {
        state.log.setState('done');
    }
    else {
        state.log.setState('failed');
    }

    state.log.show();
};

// ////////////////////////////////////////////////////////////////////////

// Whether the address is the repository that runs now, with its branches listed.
$.fn.zato.envRepo.isCurrent = function() {

    const state = $.fn.zato.envRepo.state;
    const address = $('#repo-url').val().trim();
    const currentUrl = $('#repo-url').data('current-url');

    const out = state.isConnected && (state.mode === 'switch' || state.mode === 'pull') && address === currentUrl;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The chip in the field says whether GitHub let us into the repository whose address is there, and Push and Disconnect
// stand by the button once it did.
$.fn.zato.envRepo.updateSide = function() {

    const chip = $('#connection-chip');
    const isChecked = $.fn.zato.envRepo.state.isChecked;

    chip.toggleClass('env-repo-chip-on', isChecked);
    chip.toggleClass('env-repo-chip-off', !isChecked);
    chip.text(chip.data(isChecked ? 'connected-label' : 'not-connected-label'));

    $('#disconnect-button').toggleClass('env-repo-link-disabled', !isChecked);
    $('#push-button').prop('disabled', !isChecked);

    $.fn.zato.envRepo.updateHint();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handlePush = function() {
    alert('Push clicked');
};

// ////////////////////////////////////////////////////////////////////////

// With the repository that runs now, the branch that runs is pulled and any other one is switched to.
$.fn.zato.envRepo.handleBranchChange = function() {

    const state = $.fn.zato.envRepo.state;

    if(state.mode !== 'switch' && state.mode !== 'pull') {
        return;
    }

    // Only a host switches, which restarts it, locally the branch chosen is simply pulled.
    if(!state.isHost) {
        $.fn.zato.envRepo.setMode('pull');
        return;
    }

    if(!$.fn.zato.envRepo.isCurrent()) {
        return;
    }

    const isCurrentBranch = $('#repo-branch').val() === $('#repo-url').data('current-branch');
    $.fn.zato.envRepo.setMode(isCurrentBranch ? 'pull' : 'switch');
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

// A new address starts the flow over.
$.fn.zato.envRepo.handleUrlInput = function() {

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();
    $.fn.zato.envRepo.clearFieldError();
    $.fn.zato.envRepo.setMode('connect');
};

// ////////////////////////////////////////////////////////////////////////

// The mode is connect, allow, switch or pull - the last two both read Pull, a pull of what runs now is a plain pull
// and a pull of another branch or repository switches over to it first.
$.fn.zato.envRepo.setMode = function(mode) {

    const button = $('#action-button');
    let label = 'connect-label';

    if(mode === 'allow') {
        label = 'allow-label';
    }
    else if(mode === 'pull' || mode === 'switch') {
        label = 'pull-label';
    }

    $.fn.zato.envRepo.state.mode = mode;
    button.val(button.data(label));
    button.prop('disabled', false);
    button.toggleClass('env-repo-attention', mode === 'allow');

    $.fn.zato.envRepo.updateSide();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.resetFlow = function() {

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.setBranchView('branch-placeholder');
    $('#key-help').addClass('hidden');

    state.isChecked = false;
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

    if(message) {
        $.fn.zato.envRepo.appendLine(message, null);
    }
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

    // The message of a step becomes a line once the next step is written, so it is not shown a second time.
    for(let idx = state.lineCount; idx < lines.length; idx++) {
        if(lines[idx] !== state.lastMessage) {
            $.fn.zato.envRepo.appendLine(lines[idx], null);
        }
    }

    state.lineCount = lines.length;

    if(status.message && status.message !== state.lastMessage) {

        let kind = null;

        if(status.state === 'error') {
            kind = 'error';
        }
        else if(status.state === 'ok' || status.state === 'switched' || status.state === 'disconnected' || status.state === 'pulled') {
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
    else if(mode === 'pull') {
        $.fn.zato.envRepo.handlePull();
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
    $.fn.zato.envRepo.updateHint();

    state.repo = $.fn.zato.envRepo.parseAddress(address);
    state.isQuiet = false;

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.setBranchView('branch-spinner');
    $.fn.zato.envRepo.startLog(state.repo, '');

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

// Connected - the branches take the spinner's place and Connect now means the switch to the one chosen,
// or Pull if the one chosen is the one that runs now.
$.fn.zato.envRepo.onConnected = function(status) {

    const state = $.fn.zato.envRepo.state;
    const branches = status.branches || [];

    state.isQuiet = false;
    state.isChecked = true;

    $.fn.zato.envRepo.stopAll();
    $('#key-help').addClass('hidden');

    $.fn.zato.envRepo.appendStatus(status);
    state.log.setState('done');

    // A repository with no branches is an empty one, there is nothing in it to switch to yet.
    if(!branches.length) {
        $.fn.zato.envRepo.setBranchView('branch-placeholder');
        $.fn.zato.envRepo.setMode('connect');
        return;
    }

    $.fn.zato.envRepo.fillBranches(branches);
    $.fn.zato.envRepo.setBranchView('repo-branch');

    $.fn.zato.envRepo.setMode('switch');
    $.fn.zato.envRepo.handleBranchChange();
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

    // With the App, GitHub's page for its repositories is where the browser goes, and GitHub brings it back here
    // once the repository is added, with the address waiting to be connected again.
    if(state.appState === config.appStateInstalled) {
        window.sessionStorage.setItem(config.addressKey, address);
        window.location.href = state.installUrl;
        return;
    }

    const url = $.fn.zato.envRepo.getKeyUrl(state.repo);

    // The tab opens here, within the click, or the browser would block it.
    window.open(url, '_blank', 'noopener');

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(state.repo, 'Waiting for GitHub to accept the key for ' + state.repo.full_name);

    if($('#public-key').text().trim()) {
        $('#deploy-key-link').attr('href', url);
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

$(document).ready(function() {
    $.fn.zato.envRepo.init();
});
