'use strict';

// The dashboard-wide data helpers: GET and POST against the JSON views,
// with the CSRF token Django expects on every POST. A view answers a bad
// request with {error: message} under a non-2xx status, and that message
// goes to the caller's onError handler.

(function() {

var data = {

    // Every signed-in page carries a CSRF input in the sign-out form
    csrfToken: function() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },

// ////////////////////////////////////////////////////////////////////////

    handle: function(response, onDone, onError) {
        response.json().then(function(payload) {
            if (response.ok) { onDone(payload); return; }
            onError(payload.error);
        });
    },

    get: function(url, onDone, onError) {
        var self = this;
        fetch(url, {credentials: 'same-origin'}).then(function(response) {
            self.handle(response, onDone, onError);
        });
    },

    post: function(url, body, onDone, onError) {
        var self = this;
        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': self.csrfToken()},
            body: JSON.stringify(body),
        }).then(function(response) {
            self.handle(response, onDone, onError);
        });
    },

// ////////////////////////////////////////////////////////////////////////

    // The report of last resort - a red popover on the screen's title line
    reportError: function(message) {
        shared.popover(document.querySelector('.main-topbar-line'), message, 'red');
    },
};

window.data = data;

})();
