'use strict';

(function() {

var data = {

    config: {
        unreachableMessage: 'The application is unreachable, the request never completed',
        notJsonMessage: 'The application answered with something other than JSON, ' +
            'the session may have expired - reloading the page signs you back in',

        // The host application sets this through editorView.init
        csrfToken: '',
    },

    csrfToken: function() {
        if (data.config.csrfToken !== '') { return data.config.csrfToken; }
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },

// ////////////////////////////////////////////////////////////////////////

    handle: function(response, onDone, onError) {
        var self = this;
        response.json().then(function(payload) {
            if (response.ok) { onDone(payload); return; }
            onError(payload.error);
        }, function() {

            onError(self.config.notJsonMessage);
        });
    },

    get: function(url, onDone, onError) {
        var self = this;
        fetch(url, {credentials: 'same-origin'}).then(function(response) {
            self.handle(response, onDone, onError);
        }, function() {
            onError(self.config.unreachableMessage);
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
        }, function() {
            onError(self.config.unreachableMessage);
        });
    },

// ////////////////////////////////////////////////////////////////////////

    reportError: function(message) {
        shared.popover(document.querySelector('.command-bar, .toolbar'), message, 'red');
    },
};

window.data = data;

})();
