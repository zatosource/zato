'use strict';

// Data model for the notifications screen: which chat platforms hold
// credentials, one ruleset's destinations with their delivery status,
// the live targets a platform offers right now and the fixed matrix of
// notified events. No DOM access in this file.

(function() {

var notifyModel = {

    config: {
        // Every platform the notify loop delivers to, in its fixed order
        kinds: ['teams', 'slack'],
        kindLabels: {
            'teams': 'Microsoft Teams',
            'slack': 'Slack',
        },

        // What each platform's credentials must carry - the same required
        // fields the server checks before it stores anything
        credentialFields: {
            'teams': [
                {name: 'tenant_id', label: 'Tenant id'},
                {name: 'client_id', label: 'Client id'},
                {name: 'client_secret', label: 'Client secret'},
            ],
            'slack': [
                {name: 'token', label: 'Token'},
            ],
        },

        urls: {
            rulesets: '/rules/rulesets/?object_type=ruleset',
            chatConfig: '/rules/notifications/chat-config/',
            chatConfigSave: '/rules/notifications/chat-config/save/',
            chatConfigTest: '/rules/notifications/chat-config/test/',
            targets: function(kind) { return '/rules/notifications/targets/?kind=' + kind; },
            matrix: '/rules/notifications/matrix/',
            destinations: function(id) { return '/rules/rulesets/' + id + '/destinations/'; },
            destinationAdd: function(id) { return '/rules/rulesets/' + id + '/destinations/add/'; },
            destinationDelete: function(id) { return '/rules/notifications/destinations/' + id + '/delete/'; },
        },
    },

    // Only admins manage the shared credentials - the credentials pane is
    // rendered into the page for admins alone and its presence is the flag
    isAdmin: false,

    // Every stored ruleset, and the one whose destinations show
    rulesets: [],
    rulesetId: null,
    rulesetName: '',

    // The chosen ruleset's destinations with their delivery status
    destinations: [],

    // Which platform holds credentials - never the credentials themselves
    credentials: [],

    // The live targets of the platform picked in the add row
    targets: [],

    // The fixed matrix of notified events, fetched once when first opened
    matrix: null,

// ////////////////////////////////////////////////////////////////////////

    // The screen opens on the ruleset the address names, or on the first
    // stored one, with the credentials status for admins
    load: function(onDone) {
        var self = this;
        var wanted = new URLSearchParams(window.location.search).get('ruleset');

        data.get(this.config.urls.rulesets, function(payload) {
            self.rulesets = payload.items;

            var records = payload.items;
            if (wanted !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wanted); });
            }

            if (records.length > 0) {
                self.rulesetId = records[0].id;
                self.rulesetName = records[0].name;
            }

            self.loadCredentials(function() {
                self.loadDestinations(onDone);
            });
        }, data.reportError);
    },

    // Which platforms are configured - admins only, everyone else keeps
    // the empty list and the credentials pane simply is not on their page
    loadCredentials: function(onDone) {
        if (!this.isAdmin) {
            onDone();
            return;
        }

        var self = this;
        data.get(this.config.urls.chatConfig, function(payload) {
            self.credentials = payload.items;
            onDone();
        }, data.reportError);
    },

    loadDestinations: function(onDone) {
        if (this.rulesetId === null) {
            onDone();
            return;
        }

        var self = this;
        data.get(this.config.urls.destinations(this.rulesetId), function(payload) {
            self.destinations = payload.items;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // The live picker: what channels one platform offers right now -
    // an unconfigured platform answers with a readable refusal
    loadTargets: function(kind, onDone, onError) {
        var self = this;
        this.targets = [];

        data.get(this.config.urls.targets(kind), function(payload) {
            self.targets = payload.items;
            onDone();
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    addDestination: function(kind, target, onDone, onError) {
        var self = this;
        var body = {kind: kind, target: target};

        data.post(this.config.urls.destinationAdd(this.rulesetId), body, function() {
            self.loadDestinations(onDone);
        }, onError);
    },

    deleteDestination: function(destinationId, onDone) {
        var self = this;

        data.post(this.config.urls.destinationDelete(destinationId), {}, function() {
            self.loadDestinations(onDone);
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // Stores one platform's credentials - the server encrypts them and
    // never sends them back, the status list is all the screen ever sees
    saveCredentials: function(kind, values, onDone, onError) {
        var self = this;
        var body = {kind: kind, values: values};

        data.post(this.config.urls.chatConfigSave, body, function() {
            self.loadCredentials(onDone);
        }, onError);
    },

    // The test message: admins see their credentials work before any
    // ruleset relies on them
    sendTest: function(kind, target, onDone, onError) {
        data.post(this.config.urls.chatConfigTest, {kind: kind, target: target}, onDone, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    loadMatrix: function(onDone) {
        // The matrix is fixed, one fetch serves every later opening
        if (this.matrix !== null) {
            onDone();
            return;
        }

        var self = this;
        data.get(this.config.urls.matrix, function(payload) {
            self.matrix = payload.items;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // The platforms that hold no credentials yet - only admins know,
    // everyone else gets an empty answer and no problem entries
    unconfiguredKindsInUse: function() {
        if (!this.isAdmin) { return []; }

        var configured = {};
        this.credentials.forEach(function(entry) {
            if (entry.is_configured) { configured[entry.kind] = true; }
        });

        var seen = {};
        var out = [];

        this.destinations.forEach(function(record) {
            if (configured[record.kind] === true) { return; }
            if (seen[record.kind] === true) { return; }
            seen[record.kind] = true;
            out.push(record.kind);
        });

        return out;
    },
};

window.notifyModel = notifyModel;

})();
