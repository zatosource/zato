'use strict';

(function() {

var rulesetsModel = {

    config: {
        listLimit: 200,

        urls: {
            rulesets: '/rules/rulesets/?object_type=ruleset&limit=',
            follows: '/rules/follows/',
            feed: '/rules/feed/',
            views: '/rules/views/',
            viewSave: '/rules/views/save/',
            viewDelete: '/rules/views/delete/',
            recents: '/rules/recents/',
            search: '/rules/search/?q=',
            preview: function(id) { return '/rules/rulesets/' + id + '/preview/'; },
            publish: function(id) { return '/rules/rulesets/' + id + '/publish/'; },
            rename: function(id) { return '/rules/rulesets/' + id + '/rename/'; },
            follow: function(id) { return '/rules/rulesets/' + id + '/follow/'; },
            unfollow: function(id) { return '/rules/rulesets/' + id + '/unfollow/'; },
            seen: function(id) { return '/rules/rulesets/' + id + '/seen/'; },
        },
    },

    rulesets: [],
    followedIds: {},
    feed: [],
    views: [],
    recents: [],
    searchHits: [],

// ////////////////////////////////////////////////////////////////////////

    load: function(onDone) {
        var self = this;
        var remaining = 5;

        var step = function() {
            remaining -= 1;
            if (remaining === 0) { onDone(); }
        };

        data.get(this.config.urls.rulesets + this.config.listLimit, function(payload) {
            self.rulesets = payload.items;
            step();
        }, data.reportError);

        this.loadFollows(step);
        this.loadFeed(step);
        this.loadViews(step);
        this.loadRecents(step);
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

    loadRecents: function(onDone) {
        var self = this;
        data.get(this.config.urls.recents, function(payload) {
            self.recents = payload.items;
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

    filtered: function(view, query) {
        var self = this;
        var needle = query.trim().toLowerCase();
        var out = [];

        this.rulesets.forEach(function(ruleset) {
            if (view === 'live' && ruleset.live_version === null) { return; }
            if (view === 'drafts' && self.draftVersion(ruleset) === null) { return; }
            if (view === 'followed' && !self.isFollowed(ruleset.id)) { return; }

            var hits = self.hitsFor(ruleset.id);

            if (needle === '') {
                out.push({ruleset: ruleset, hits: hits});
                return;
            }

            var nameHit = ruleset.name.toLowerCase().indexOf(needle) > -1;
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

    saveView: function(name, view, query, onDone, onError) {
        var self = this;
        data.post(this.config.urls.viewSave, {name: name, payload: {view: view, query: query}}, function() {
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
