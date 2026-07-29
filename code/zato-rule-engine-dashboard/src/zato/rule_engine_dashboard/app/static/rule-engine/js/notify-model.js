'use strict';

(function() {

var notifyModel = {

    config: {
        kinds: ['teams', 'slack'],
        kindLabels: {
            'teams': 'Microsoft Teams',
            'slack': 'Slack',
        },

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

    isAdmin: false,

    rulesets: [],
    rulesetId: null,
    rulesetName: '',

    destinations: [],

    credentials: [],

    targets: [],

    matrix: null,

// ////////////////////////////////////////////////////////////////////////

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

    saveCredentials: function(kind, values, onDone, onError) {
        var self = this;
        var body = {kind: kind, values: values};

        data.post(this.config.urls.chatConfigSave, body, function() {
            self.loadCredentials(onDone);
        }, onError);
    },

    sendTest: function(kind, target, onDone, onError) {
        data.post(this.config.urls.chatConfigTest, {kind: kind, target: target}, onDone, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    loadMatrix: function(onDone) {
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
