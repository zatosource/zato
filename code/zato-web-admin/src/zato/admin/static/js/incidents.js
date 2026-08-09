// The incident detail screen - the approve, reject and resubmit decisions,
// each confirmed in a popup before its service runs.

$.fn.zato.incidents = {};

$.fn.zato.incidents.config = {
    actionUrl: '',
    listUrl: '',
    name: '',
    autoAction: '',
    prompts: {
        approve: 'Approve this incident and run its remediation?',
        reject: 'Reject this incident?',
        resubmit: 'Resubmit the failed requests through this connection?'
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.incidents.currentAction = '';

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.incidents.openModal = function(action) {

    var config = $.fn.zato.incidents.config;
    $.fn.zato.incidents.currentAction = action;

    var modalText = document.getElementById('incidents-modal-text');
    modalText.textContent = config.prompts[action];

    // Only a rejection carries a reason.
    var reason = document.getElementById('incidents-modal-reason');

    if(action === 'reject') {
        reason.classList.remove('detail-hidden');
    }
    else {
        reason.classList.add('detail-hidden');
    }

    var error = document.getElementById('incidents-modal-error');
    error.classList.add('detail-hidden');

    var overlay = document.getElementById('incidents-modal-overlay');
    overlay.classList.remove('detail-hidden');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.incidents.closeModal = function() {
    var overlay = document.getElementById('incidents-modal-overlay');
    overlay.classList.add('detail-hidden');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.incidents.confirm = function() {

    var config = $.fn.zato.incidents.config;
    var action = $.fn.zato.incidents.currentAction;

    var data = {
        action: action,
        name: config.name
    };

    if(action === 'reject') {
        var reason = document.getElementById('incidents-modal-reason');
        data.reason = reason.value;
    }

    $.ajax({
        url: config.actionUrl,
        type: 'POST',
        data: data,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(response) {

            if(typeof response === 'string') {
                response = JSON.parse(response);
            }

            // A service that could not act answers with an error inside a 200.
            if(response.error) {
                $.fn.zato.incidents.showError(response.error);
                return;
            }

            // The page reflects the new status once it reloads.
            window.location.href = window.location.pathname + window.location.search.replace(/[?&]action=[^&]*/, '');
        },
        error: function(request) {
            $.fn.zato.incidents.showError(request.responseText);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.incidents.showError = function(text) {
    var error = document.getElementById('incidents-modal-error');
    error.textContent = text;
    error.classList.remove('detail-hidden');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.incidents.init = function(config) {

    $.fn.zato.incidents.config.actionUrl = config.actionUrl;
    $.fn.zato.incidents.config.listUrl = config.listUrl;
    $.fn.zato.incidents.config.name = config.name;
    $.fn.zato.incidents.config.autoAction = config.autoAction;

    var buttons = [
        ['incidents-approve', 'approve'],
        ['incidents-reject', 'reject'],
        ['incidents-resubmit', 'resubmit']
    ];

    for(var buttonIdx = 0; buttonIdx < buttons.length; buttonIdx++) {

        var buttonId = buttons[buttonIdx][0];
        var buttonAction = buttons[buttonIdx][1];
        var button = document.getElementById(buttonId);

        // Only the buttons the incident's status allows are on the page.
        if(button) {
            button.addEventListener('click', $.fn.zato.incidents.makeOpenHandler(buttonAction));
        }
    }

    var confirmButton = document.getElementById('incidents-modal-confirm');
    confirmButton.addEventListener('click', $.fn.zato.incidents.confirm);

    var cancelButton = document.getElementById('incidents-modal-cancel');
    cancelButton.addEventListener('click', $.fn.zato.incidents.closeModal);

    // A notification link may arrive with the action to open the popup for.
    if(config.autoAction === 'resubmit') {

        var resubmitButton = document.getElementById('incidents-resubmit');

        if(resubmitButton) {
            $.fn.zato.incidents.openModal('resubmit');
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.incidents.makeOpenHandler = function(action) {

    function openHandler() {
        $.fn.zato.incidents.openModal(action);
    }

    return openHandler;
};
