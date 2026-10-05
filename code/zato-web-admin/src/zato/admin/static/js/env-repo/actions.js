// What happens to the repository that runs now - the switch to another branch or repository,
// the pull that brings its checkout up to date, and the disconnect that lets go of it.

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.handleSwitch = function() {

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.clearStatus();

    state.isQuiet = false;

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(state.repo, '');

    $.fn.zato.envRepo.sendRequest('switch', function() {
        $.fn.zato.envRepo.pollStatus(['switching'], $.fn.zato.envRepo.onSwitchDone);
    }, function(errorMessage) {
        $.fn.zato.envRepo.onSwitchDone({state: 'error', message: errorMessage, lines: []});
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onSwitchDone = function(status) {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.appendStatus(status);

    // The host restarts the environment after this state and its own page takes over once it is up.
    if(status.state === 'switching') {
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

// Brings the checkout of the repository that runs now up to date, nothing restarts.
$.fn.zato.envRepo.handlePull = function() {

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.clearStatus();

    state.isQuiet = false;
    state.repo = $.fn.zato.envRepo.parseAddress($('#repo-url').val().trim());

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(state.repo, '');

    $.fn.zato.envRepo.sendRequest('pull', function() {
        $.fn.zato.envRepo.pollStatus(['pulled'], $.fn.zato.envRepo.onPullDone);
    }, function(errorMessage) {
        $.fn.zato.envRepo.onPullDone({state: 'error', message: errorMessage, lines: []});
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onPullDone = function(status) {

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.appendStatus(status);
    state.log.setState(status.state === 'pulled' ? 'done' : 'failed');

    $.fn.zato.envRepo.setMode('pull');
};

// ////////////////////////////////////////////////////////////////////////

// Disconnects from the repository entirely - the App's access on GitHub is taken away, the checkout and current.json
// are removed, a host goes back to the public blueprint. A spinner stands where the link was until it is done,
// then the page is as it was before anything was connected.
$.fn.zato.envRepo.handleDisconnect = function(e) {

    e.preventDefault();

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.clearStatus();

    // The panel is left alone, so what the poll finds does not go into it.
    state.isQuiet = true;

    $('#disconnect-button').addClass('env-repo-link-disabled');
    $('#disconnect-spinner').removeClass('hidden');

    $.fn.zato.envRepo.sendRequest('disconnect', function() {
        $.fn.zato.envRepo.pollStatus(['switching', 'disconnected'], $.fn.zato.envRepo.onDisconnectDone);
    }, function(errorMessage) {
        $.fn.zato.envRepo.onDisconnectDone({state: 'error', message: errorMessage, lines: []});
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.onDisconnectDone = function(status) {

    const state = $.fn.zato.envRepo.state;

    state.isQuiet = false;
    $('#disconnect-spinner').addClass('hidden');

    // A host restarts the environment with the public blueprint, the loading page takes over from here.
    if(status.state === 'switching') {
        $.fn.zato.envRepo.waitForDeployPage();
        return;
    }

    if(status.state !== 'disconnected') {
        $.fn.zato.envRepo.showStatus(status.message, false);
        $.fn.zato.envRepo.updateSide();
        return;
    }

    // Nothing of the repository is left, here or on GitHub, and the page is as it was before anything was connected.
    const config = $.fn.zato.envRepo.config;

    state.isConnected = false;
    state.knownRepos = null;

    if(state.appState === config.appStateInstalled) {
        state.appState = config.appStateCreated;
        state.installUrl = $('#repo-form').data('new-install-url');
    }

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.resetFlow();
    $.fn.zato.envRepo.isCreating(true);

    $('#repo-url').val('').data('current-url', '').data('current-branch', '');
    $('#repo-list').empty();

    $.fn.zato.envRepo.setMode('connect');
};

