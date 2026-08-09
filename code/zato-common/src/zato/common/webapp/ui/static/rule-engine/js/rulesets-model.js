'use strict';

(function() {

var rulesetsModel = {

    config: {
        listLimit: 200,

        // The host application passes every URL through rulesetsView.init - only the list
        // and the preview are required, the rest are the collaboration endpoints the rule
        // engine dashboard has and an embedding host may not
        urls: {},

        // What a ruleset is called on the screen when its stored name is technical -
        // a map from the stored name to the label the browser shows and searches by
        rulesetLabels: {},

        // Whether a typed query matches a ruleset by its own name - a host whose one
        // ruleset is a fixture wants the query to reach the rules inside it only
        matchRulesetNames: true,
    },

    rulesets: [],
    followedIds: {},
    feed: [],
    views: [],
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
        var urls = this.config.urls;

        // Only the endpoints the host actually has take part in the load
        var steps = 1;
        if (urls.follows !== undefined) { steps += 1; }
        if (urls.feed !== undefined) { steps += 1; }
        if (urls.views !== undefined) { steps += 1; }

        var remaining = steps;
        var step = function() {
            remaining -= 1;
            if (remaining === 0) { onDone(); }
        };

        data.get(urls.rulesets + this.config.listLimit, function(payload) {
            self.rulesets = payload.items;
            step();
        }, data.reportError);

        if (urls.follows !== undefined) { this.loadFollows(step); }
        if (urls.feed !== undefined) { this.loadFeed(step); }
        if (urls.views !== undefined) { this.loadViews(step); }
    },

    loadFollows: function(onDone) {
        var self = this;
        data.get(this.config.urls.follows, function(payload) {
            self.followedIds = {};
            payload.items.forEach(function(item) { self.followedIds[item.definition_id] = true; });
            onDone();
        }, data.reportError);
    },

    loadFeed: function(onDone) {
        var self = this;
        data.get(this.config.urls.feed, function(payload) {
            self.feed = payload.items;
            onDone();
        }, data.reportError);
    },

    loadViews: function(onDone) {
        var self = this;
        data.get(this.config.urls.views, function(payload) {
            self.views = payload.items;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    byId: function(id) {
        var out = this.rulesets.filter(function(candidate) { return candidate.id === id; })[0];
        return out;
    },

    isFollowed: function(id) {
        return this.followedIds[id] === true;
    },

    draftVersion: function(ruleset) {
        if (ruleset.live_version === null) { return ruleset.current_version; }
        if (ruleset.current_version > ruleset.live_version) { return ruleset.current_version; }
        return null;
    },

// ////////////////////////////////////////////////////////////////////////

    counts: function() {
        var self = this;
        var out = {live: 0, draft: 0, followed: 0, total: this.rulesets.length};

        this.rulesets.forEach(function(ruleset) {
            if (ruleset.live_version !== null) { out.live += 1; }
            if (self.draftVersion(ruleset) !== null) { out.draft += 1; }
            if (self.isFollowed(ruleset.id)) { out.followed += 1; }
        });

        return out;
    },

    filtered: function(filters, query) {
        var self = this;
        var needle = query.trim().toLowerCase();
        var out = [];

        this.rulesets.forEach(function(ruleset) {
            if (filters.live && ruleset.live_version === null) { return; }
            if (filters.draft && self.draftVersion(ruleset) === null) { return; }
            if (filters.followed && !self.isFollowed(ruleset.id)) { return; }

            var hits = self.hitsFor(ruleset.id);

            if (needle === '') {
                out.push({ruleset: ruleset, hits: hits});
                return;
            }

            // Both the stored name and the label it shows under count as a match,
            // unless the host keeps the query away from ruleset names altogether
            var names = ruleset.name + ' ' + self.displayName(ruleset.name);
            var nameHit = self.config.matchRulesetNames && names.toLowerCase().indexOf(needle) > -1;
            if (nameHit || hits.length > 0) {
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

    preview: function(id, onDone) {
        data.get(this.config.urls.preview(id), onDone, data.reportError);
    },

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
                    conditionCount: entry.conditions.length,
                    actionCount: entry.then.length,
                });
            });

            out.sort(function(left, right) { return left.name.localeCompare(right.name); });

            self.rulesCache[id] = out;
            onDone(out);
        }, data.reportError);
    },

    publish: function(id, version, onDone, onError) {
        data.post(this.config.urls.publish(id), {version: version}, onDone, onError);
    },

    renamePreview: function(id, newName, onDone, onError) {
        data.post(this.config.urls.rename(id), {new_name: newName, dry_run: true}, onDone, onError);
    },

    renameApply: function(id, newName, onDone, onError) {
        var self = this;
        data.post(this.config.urls.rename(id), {new_name: newName, dry_run: false}, function(report) {

            self.byId(id).name = report.new_name;
            onDone(report);
        }, onError);
    },

    follow: function(id, onDone) {
        var self = this;
        data.post(this.config.urls.follow(id), {}, function(payload) {
            self.followedIds[payload.definition_id] = true;
            onDone();
        }, data.reportError);
    },

    unfollow: function(id, onDone) {
        var self = this;
        data.post(this.config.urls.unfollow(id), {}, function(payload) {
            delete self.followedIds[payload.definition_id];
            onDone();
        }, data.reportError);
    },

    markSeen: function(id, onDone) {
        var self = this;
        data.post(this.config.urls.seen(id), {}, function() {
            self.loadFeed(onDone);
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    savedViews: function() {
        return this.views;
    },

    saveView: function(name, payload, onDone, onError) {
        var self = this;
        data.post(this.config.urls.viewSave, {name: name, payload: payload}, function() {
            self.loadViews(onDone);
        }, onError);
    },

    deleteView: function(name, onDone) {
        var self = this;
        data.post(this.config.urls.viewDelete, {name: name}, function() {
            self.loadViews(onDone);
        }, data.reportError);
    },
};

window.rulesetsModel = rulesetsModel;

})();
