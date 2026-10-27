zatoPortal.config = {
    specUrl: '/api-portal/openapi.json',
    logoutUrl: '/api-portal/logout',
    statusUnauthorized: 401,
    emptyText: 'No endpoints available',
    networkErrorText: 'The portal could not be reached',
    loadingId: 'portal-loading',
    statusId: 'portal-status',
    statusTextId: 'portal-status-text',
    workspaceId: 'portal-workspace',
    navigationId: 'portal-navigation',
    contentId: 'portal-content',
    filterId: 'portal-filter',
    logoutId: 'portal-logout',
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.init = function() {

    // The history of invocations does not outlive the session it was made in
    var logout = document.getElementById(zatoPortal.config.logoutId);
    logout.addEventListener('click', zatoPortal.history.clear);

    fetch(zatoPortal.config.specUrl, {cache: 'no-store'}).then(zatoPortal.onResponse, zatoPortal.onNetworkError);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.onNetworkError = function() {
    zatoPortal.showStatus(zatoPortal.config.networkErrorText);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.onResponse = function(response) {

    // A session whose credentials are no longer accepted signs in again ..
    if(response.status === zatoPortal.config.statusUnauthorized) {
        zatoPortal.signOut();
        return;
    }

    // .. any other failure shows what the portal replied with ..
    if(!response.ok) {
        response.text().then(zatoPortal.showStatus);
        return;
    }

    // .. and a document is rendered.
    response.json().then(zatoPortal.show);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.signOut = function() {
    zatoPortal.links.remember();
    zatoPortal.history.clear();
    window.location.replace(zatoPortal.config.logoutUrl);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.show = function(apiDocument) {

    zatoPortal.hideLoading();

    var groups = zatoPortal.render.buildGroups(apiDocument);

    if(groups.length === 0) {
        zatoPortal.showStatus(zatoPortal.config.emptyText);
        return;
    }

    // Try-it requests go to the relay the document names as its only server ..
    var firstServer = apiDocument.servers[0];
    zatoPortal.state.relayBase = firstServer.url;
    zatoPortal.state.components = apiDocument.components.schemas;
    zatoPortal.state.groups = groups;

    // .. every group is built once, so that edited requests and their responses stay in place ..
    var navigation = document.getElementById(zatoPortal.config.navigationId);
    var content = document.getElementById(zatoPortal.config.contentId);

    var currentSection = '';

    for(var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
        var group = groups[groupIndex];

        // The groups of a section are listed under its heading, which precedes the first of them
        if(group.section !== currentSection) {
            currentSection = group.section;

            if(currentSection !== '') {
                var navigationSection = zatoPortal.render.buildNavigationSection(currentSection);
                navigation.appendChild(navigationSection);
            }
        }

        var navigationGroup = zatoPortal.render.buildNavigationGroup(group);
        navigation.appendChild(navigationGroup);

        var section = zatoPortal.render.buildSection(group);
        content.appendChild(section);

        zatoPortal.layouts.apply(section, group);
    }

    var filter = document.getElementById(zatoPortal.config.filterId);
    filter.addEventListener('input', zatoPortal.render.onFilterInput);

    // .. and the operation shown is the one the address links to, or the first group otherwise.
    zatoPortal.links.init();
    zatoPortal.links.showInitial(groups[0]);

    var workspace = document.getElementById(zatoPortal.config.workspaceId);
    workspace.hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.showStatus = function(text) {

    zatoPortal.hideLoading();

    var container = document.getElementById(zatoPortal.config.statusId);
    var textElement = document.getElementById(zatoPortal.config.statusTextId);

    textElement.textContent = text;
    container.hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.hideLoading = function() {

    var container = document.getElementById(zatoPortal.config.loadingId);
    container.hidden = true;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.init();
