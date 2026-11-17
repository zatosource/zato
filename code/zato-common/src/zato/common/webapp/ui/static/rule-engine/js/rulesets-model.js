'use strict';

(function() {

var rulesetsModel = {

    config: {
        listLimit: 200,

        // The host application passes the list, search and preview URLs through rulesetsView.init
        urls: {},

        // What a ruleset is called on the screen when its stored name is technical -
        // a map from the stored name to the label the browser shows
        rulesetLabels: {},
    },

    rulesets: [],
    searchHits: [],
    rulesCache: {},

// ////////////////////////////////////////////////////////////////////////

    // The name a ruleset goes by on the screen - its own unless the host relabels it
    displayName: function(name) {
        var label = this.config.rulesetLabels[name];
        if (label === undefined) { label = name; }
        return label;
    },

// ////////////////////////////////////////////////////////////////////////

    load: function(onDone) {
        var self = this;

        data.get(this.config.urls.rulesets + this.config.listLimit, function(payload) {
            self.rulesets = payload.items;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // A typed query reaches the rules inside each ruleset, never the ruleset names
    filtered: function(query) {
        var self = this;
        var needle = query.trim();
        var out = [];

        this.rulesets.forEach(function(ruleset) {
            var hits = self.hitsFor(ruleset.id);

            if (needle === '' || hits.length > 0) {
                out.push({ruleset: ruleset, hits: hits});
            }
        });

        return out;
    },

    hitsFor: function(id) {
        var out = this.searchHits.filter(function(hit) { return hit.definition_id === id; });
        return out;
    },

    search: function(query, onDone) {
        var self = this;

        if (query.trim() === '') {
            this.searchHits = [];
            onDone();
            return;
        }

        data.get(this.config.urls.search + encodeURIComponent(query.trim()), function(payload) {
            self.searchHits = payload.items;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // The rules one set is made of, kept once fetched so reopening a row is instant.
    cachedRules: function(id) {
        if (this.rulesCache[id] === undefined) { return null; }
        return this.rulesCache[id];
    },

    // A host that changed a rule behind the panel drops the cache, so the next opening refetches
    dropCachedRules: function(id) {
        delete this.rulesCache[id];
    },

    rules: function(id, onDone) {
        var self = this;
        var cached = this.cachedRules(id);

        if (cached !== null) {
            onDone(cached);
            return;
        }

        data.get(this.config.urls.preview(id), function(payload) {
            var documents = payload.document.documents;

            // A set stored before it ever got a rule carries no documents at all.
            if (documents === undefined) { documents = {}; }

            var out = [];
            Object.keys(documents).forEach(function(key) {
                var entry = documents[key];

                // Documents stored before rules could be deactivated carry no flag at all
                var isActive = entry.is_active !== false;

                out.push({
                    key: key,
                    name: entry.name,
                    docs: entry.docs,
                    isActive: isActive,
                });
            });

            out.sort(function(left, right) { return left.name.localeCompare(right.name); });

            self.rulesCache[id] = out;
            onDone(out);
        }, data.reportError);
    },
};

window.rulesetsModel = rulesetsModel;

})();
