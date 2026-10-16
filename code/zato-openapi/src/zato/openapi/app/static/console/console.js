zatoConsole.config = {
    specUrl: '/openapi/console/openapi.json',
    logoutUrl: '/openapi/console/logout',
    statusUnauthorized: 401,
    emptyText: 'No endpoints available',
    networkErrorText: 'The console could not be reached',
    loadingId: 'console-loading',
    statusId: 'console-status',
    statusTextId: 'console-status-text',
    workspaceId: 'console-workspace',
    navigationId: 'console-navigation',
    contentId: 'console-content',
    filterId: 'console-filter',
    logoutId: 'console-logout',
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.init = function() {

    // The history of invocations does not outlive the session it was made in
    var logout = document.getElementById(zatoConsole.config.logoutId);
    logout.addEventListener('click', zatoConsole.history.clear);

    fetch(zatoConsole.config.specUrl, {cache: 'no-store'}).then(zatoConsole.onResponse, zatoConsole.onNetworkError);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.onNetworkError = function() {
    zatoConsole.showStatus(zatoConsole.config.networkErrorText);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.onResponse = function(response) {

    // A session whose credentials are no longer accepted signs in again ..
    if(response.status === zatoConsole.config.statusUnauthorized) {
        zatoConsole.signOut();
        return;
    }

    // .. any other failure shows what the console replied with ..
    if(!response.ok) {
        response.text().then(zatoConsole.showStatus);
        return;
    }

    // .. and a document is rendered.
    response.json().then(zatoConsole.show);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.signOut = function() {
    zatoConsole.links.remember();
    zatoConsole.history.clear();
    window.location.replace(zatoConsole.config.logoutUrl);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.show = function(apiDocument) {

    zatoConsole.hideLoading();

    var groups = zatoConsole.render.buildGroups(apiDocument);

    if(groups.length === 0) {
        zatoConsole.showStatus(zatoConsole.config.emptyText);
        return;
    }

    // Try-it requests go to the relay the document names as its only server ..
    var firstServer = apiDocument.servers[0];
    zatoConsole.state.relayBase = firstServer.url;
    zatoConsole.state.components = apiDocument.components.schemas;
    zatoConsole.state.groups = groups;

    // .. every group is built once, so that edited requests and their responses stay in place ..
    var navigation = document.getElementById(zatoConsole.config.navigationId);
    var content = document.getElementById(zatoConsole.config.contentId);

    var currentSection = '';

    for(var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
        var group = groups[groupIndex];

        // The groups of a section are listed under its heading, which precedes the first of them
        if(group.section !== currentSection) {
            currentSection = group.section;

            if(currentSection !== '') {
                var navigationSection = zatoConsole.render.buildNavigationSection(currentSection);
                navigation.appendChild(navigationSection);
            }
        }

        var navigationGroup = zatoConsole.render.buildNavigationGroup(group);
        navigation.appendChild(navigationGroup);

        var section = zatoConsole.render.buildSection(group);
        content.appendChild(section);

        zatoConsole.layouts.apply(section, group);
    }

    var filter = document.getElementById(zatoConsole.config.filterId);
    filter.addEventListener('input', zatoConsole.render.onFilterInput);

    // .. and the operation shown is the one the address links to, or the first group otherwise.
    zatoConsole.links.init();
    zatoConsole.links.showInitial(groups[0]);

    var workspace = document.getElementById(zatoConsole.config.workspaceId);
    workspace.hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.showStatus = function(text) {

    zatoConsole.hideLoading();

    var container = document.getElementById(zatoConsole.config.statusId);
    var textElement = document.getElementById(zatoConsole.config.statusTextId);

    textElement.textContent = text;
    container.hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.hideLoading = function() {

    var container = document.getElementById(zatoConsole.config.loadingId);
    container.hidden = true;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.init();
