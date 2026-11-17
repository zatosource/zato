'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

rulesetsView.clearAll = function() {
    this.query = '';
    this.element('#rulesets-search').value = '';
    this.applyFilters();
};

// The query's place in the address bar, so a filtered listing can be bookmarked -
// only for a host that named the parameter to keep it under
rulesetsView.writeQueryToURL = function() {
    if (this.config.queryURLKey === null) { return; }

    var params = new URLSearchParams(window.location.search);
    var query = this.query.trim();

    if (query === '') {
        params.delete(this.config.queryURLKey);
    }
    else {
        params.set(this.config.queryURLKey, query);
    }

    history.replaceState(null, '', '?' + params.toString());
};

// Every query change lands here: the hits come from the server, the rest is local
rulesetsView.applyFilters = function() {
    var self = this;

    this.writeQueryToURL();

    rulesetsModel.search(this.query, function() {
        self.renderList();
        shared.initTips();
    });
};

rulesetsView.setQuery = function(value) {
    var self = this;

    this.query = value;

    if (this.searchTimer !== null) { clearTimeout(this.searchTimer); }
    this.searchTimer = setTimeout(function() {
        self.searchTimer = null;
        self.applyFilters();
    }, this.config.searchDelayMilliseconds);
};

// ////////////////////////////////////////////////////////////////////////

// Bound from rulesetsView.init, after the host handed over its container and config
rulesetsView.initFilter = function() {
    var self = this;

    var input = this.element('#rulesets-search');
    var clear = this.element('#rulesets-clear');

    // The badge waits for the first render to say whether there is anything to clear
    clear.textContent = this.config.clearLabel;
    clear.style.visibility = 'hidden';

    input.addEventListener('input', function(event) { self.setQuery(event.target.value); });

    input.addEventListener('keydown', function(event) {
        if (event.key !== 'Escape') { return; }

        event.stopPropagation();
        input.blur();
    });
};

// ////////////////////////////////////////////////////////////////////////

})();
