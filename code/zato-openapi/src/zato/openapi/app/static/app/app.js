zatoApp.config = {
    specUrl: '/openapi.json',
    logoutUrl: '/logout',
    statusUnauthorized: 401,
    emptyText: 'No endpoints available',
    networkErrorText: 'The server could not be reached',
    loadingId: 'app-loading',
    statusId: 'app-status',
    statusTextId: 'app-status-text',
    workspaceId: 'app-workspace',
    navigationId: 'app-navigation',
    contentId: 'app-content',
    filterId: 'app-filter',
    logoutId: 'app-logout',
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.init = function() {

    // The history of invocations does not outlive the session it was made in
    var logout = document.getElementById(zatoApp.config.logoutId);
    logout.addEventListener('click', zatoApp.history.clear);

    fetch(zatoApp.config.specUrl, {cache: 'no-store'}).then(zatoApp.onResponse, zatoApp.onNetworkError);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.onNetworkError = function() {
    zatoApp.showStatus(zatoApp.config.networkErrorText);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.onResponse = function(response) {

    // A session whose credentials are no longer accepted signs in again ..
    if(response.status === zatoApp.config.statusUnauthorized) {
        zatoApp.signOut();
        return;
    }

    // .. any other failure shows what the app replied with ..
    if(!response.ok) {
        response.text().then(zatoApp.showStatus);
        return;
    }

    // .. and a document is rendered.
    response.json().then(zatoApp.show);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.signOut = function() {
    zatoApp.links.remember();
    zatoApp.history.clear();
    window.location.replace(zatoApp.config.logoutUrl);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.show = function(apiDocument) {

    zatoApp.hideLoading();

    var groups = zatoApp.render.buildGroups(apiDocument);

    if(groups.length === 0) {
        zatoApp.showStatus(zatoApp.config.emptyText);
        return;
    }

    // Try-it requests go to the relay the document names as its only server ..
    var firstServer = apiDocument.servers[0];
    zatoApp.state.relayBase = firstServer.url;
    zatoApp.state.components = apiDocument.components.schemas;
    zatoApp.state.groups = groups;

    // .. every group is built once, so that edited requests and their responses stay in place ..
    var navigation = document.getElementById(zatoApp.config.navigationId);
    var content = document.getElementById(zatoApp.config.contentId);

    var currentSection = '';

    for(var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
        var group = groups[groupIndex];

        // The groups of a section are listed under its heading, which precedes the first of them
        if(group.section !== currentSection) {
            currentSection = group.section;

            if(currentSection !== '') {
                var navigationSection = zatoApp.render.buildNavigationSection(currentSection);
                navigation.appendChild(navigationSection);
            }
        }

        var navigationGroup = zatoApp.render.buildNavigationGroup(group);
        navigation.appendChild(navigationGroup);

        var section = zatoApp.render.buildSection(group);
        content.appendChild(section);

        zatoApp.layouts.apply(section, group);
    }

    var filter = document.getElementById(zatoApp.config.filterId);
    filter.addEventListener('input', zatoApp.render.onFilterInput);

    // .. and the operation shown is the one the address links to, or the first group otherwise.
    zatoApp.links.init();
    zatoApp.links.showInitial(groups[0]);

    var workspace = document.getElementById(zatoApp.config.workspaceId);
    workspace.hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.showStatus = function(text) {

    zatoApp.hideLoading();

    var container = document.getElementById(zatoApp.config.statusId);
    var textElement = document.getElementById(zatoApp.config.statusTextId);

    textElement.textContent = text;
    container.hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.hideLoading = function() {

    var container = document.getElementById(zatoApp.config.loadingId);
    container.hidden = true;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.init();
