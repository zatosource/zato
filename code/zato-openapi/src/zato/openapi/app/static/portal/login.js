var zatoLogin = {};

zatoLogin.config = {
    authTypeId: 'auth-type',
    fieldsSelector: '.portal-login-fields',
    toggleSelector: '.portal-secret-toggle',
    inputSelector: 'input',
    authTypeAttribute: 'data-auth-type',
    passwordType: 'password',
    textType: 'text',
    showText: 'Show',
    hideText: 'Hide',
    linkStorageKey: 'zato.openapi.portal.link',
    historyKeyPrefix: 'zato.openapi.portal.history.',
};

// ////////////////////////////////////////////////////////////////////////

zatoLogin.clearHistory = function() {

    var keys = Object.keys(sessionStorage);

    for(var keyIndex = 0; keyIndex < keys.length; keyIndex++) {
        var key = keys[keyIndex];

        if(key.startsWith(zatoLogin.config.historyKeyPrefix)) {
            sessionStorage.removeItem(key);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoLogin.init = function() {

    // Whoever signs in next starts with no invocations of anyone signed in before in this tab
    zatoLogin.clearHistory();

    // The redirect to this page keeps the link to an operation, which the portal follows after signing in
    var hash = window.location.hash;

    if(hash !== '') {
        sessionStorage.setItem(zatoLogin.config.linkStorageKey, hash);
    }

    var select = document.getElementById(zatoLogin.config.authTypeId);
    select.addEventListener('change', zatoLogin.onAuthTypeChange);

    var toggles = document.querySelectorAll(zatoLogin.config.toggleSelector);

    for(var toggleIndex = 0; toggleIndex < toggles.length; toggleIndex++) {
        toggles[toggleIndex].addEventListener('click', zatoLogin.onToggleClick);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoLogin.onAuthTypeChange = function(event) {

    var authType = event.target.value;
    var fieldsets = document.querySelectorAll(zatoLogin.config.fieldsSelector);

    // A disabled fieldset is neither validated nor submitted, so only the chosen type's fields are sent ..
    for(var fieldsetIndex = 0; fieldsetIndex < fieldsets.length; fieldsetIndex++) {
        var fieldset = fieldsets[fieldsetIndex];
        var isChosen = fieldset.getAttribute(zatoLogin.config.authTypeAttribute) === authType;

        fieldset.hidden = !isChosen;
        fieldset.disabled = !isChosen;

        // .. and the first of them is where typing continues.
        if(isChosen) {
            var firstInput = fieldset.querySelector(zatoLogin.config.inputSelector);
            firstInput.focus();
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoLogin.onToggleClick = function(event) {

    var button = event.currentTarget;
    var input = button.parentNode.querySelector(zatoLogin.config.inputSelector);
    var isConcealed = input.type === zatoLogin.config.passwordType;

    if(isConcealed) {
        input.type = zatoLogin.config.textType;
        button.textContent = zatoLogin.config.hideText;
    }
    else {
        input.type = zatoLogin.config.passwordType;
        button.textContent = zatoLogin.config.showText;
    }

    input.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoLogin.init();
