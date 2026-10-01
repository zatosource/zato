// What happens to the repository that runs now - the switch to another branch or repository,
// the pull that brings its checkout up to date, and the disconnect that lets go of it.

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

// Brings the checkout of the repository that runs now up to date, nothing restarts.
$.fn.zato.envRepo.handlePull = function() {

    const state = $.fn.zato.envRepo.state;

    $.fn.zato.envRepo.stopAll();
    $.fn.zato.envRepo.clearStatus();

    state.isQuiet = false;
    state.repo = $.fn.zato.envRepo.parseAddress($('#repo-url').val().trim());

    $('#action-button').prop('disabled', true);
    $.fn.zato.envRepo.startLog(state.repo, 'Pulling ' + state.repo.full_name);

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

