zatoConsole.links = {};

zatoConsole.links.config = {
    hashPrefix: '#',
    storageKey: 'zato.openapi.console.link',
};

zatoConsole.links.state = {
    entryIdsByHash: {},
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getHash = function(entry) {
    var out = zatoConsole.links.config.hashPrefix + entry.method + entry.path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getUrl = function(entry) {

    var address = window.location;
    var hash = zatoConsole.links.getHash(entry);

    var out = address.origin + address.pathname + address.search + hash;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.init = function() {

    var entriesById = zatoConsole.state.entriesById;
    var entryIds = Object.keys(entriesById);

    for(var entryIndex = 0; entryIndex < entryIds.length; entryIndex++) {
        var entryId = entryIds[entryIndex];
        var hash = zatoConsole.links.getHash(entriesById[entryId]);

        zatoConsole.links.state.entryIdsByHash[hash] = entryId;
    }

    window.addEventListener('hashchange', zatoConsole.links.onHashChange);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.remember = function() {

    var hash = window.location.hash;

    // A link opened before signing in is followed once the console is shown again
    if(hash !== '') {
        sessionStorage.setItem(zatoConsole.links.config.storageKey, hash);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getEntryId = function(hash) {

    var entryIdsByHash = zatoConsole.links.state.entryIdsByHash;
    var decoded = '';

    // A link comes from outside the console, and its escapes can be malformed
    try {
        decoded = decodeURIComponent(hash);
    }
    catch(error) {
        return '';
    }

    if(decoded in entryIdsByHash) {
        return entryIdsByHash[decoded];
    }

    return '';
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.showInitial = function(firstGroup) {

    var config = zatoConsole.links.config;
    var hash = window.location.hash;

    // A link that led to the sign-in page is the one followed, unless the address has a link of its own ..
    var remembered = sessionStorage.getItem(config.storageKey);
    sessionStorage.removeItem(config.storageKey);

    if(hash === '') {
        if(remembered !== null) {
            hash = remembered;
        }
    }

    var entryId = zatoConsole.links.getEntryId(hash);

    // .. an operation linked to is shown as it would be when chosen in the navigation ..
    if(entryId !== '') {
        zatoConsole.links.showEntry(entryId);
        return;
    }

    // .. and without one the first group is shown.
    zatoConsole.render.selectGroup(firstGroup.name);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.showEntry = function(entryId) {

    var entry = zatoConsole.state.entriesById[entryId];

    zatoConsole.render.selectGroup(entry.group);
    zatoConsole.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.update = function(entryId) {

    var entry = zatoConsole.state.entriesById[entryId];
    var hash = zatoConsole.links.getHash(entry);

    // The address always names the operation shown, without adding to the browser's history
    if(window.location.hash !== hash) {
        history.replaceState(null, '', hash);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.onHashChange = function() {

    var entryId = zatoConsole.links.getEntryId(window.location.hash);

    if(entryId !== '') {
        zatoConsole.links.showEntry(entryId);
    }
};
