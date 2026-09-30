// How the page talks to the server - sends its requests, polls for the status they leave behind,
// and waits for the loading page once a host restarts the environment.

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

    if(state.keyHelpTimer) {
        clearTimeout(state.keyHelpTimer);
        state.keyHelpTimer = null;
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
