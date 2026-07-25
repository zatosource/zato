'use strict';

// The sentence bar of the decision table: one selected column read back
// as a near-natural sentence, composed from the same parsed cells the
// grid draws. Augments the tableView namespace from table-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

tableView.formatIntervalPhrase = function(parsed) {
    if (parsed.low === parsed.high) { return String(parsed.low); }
    var out = 'between ' + parsed.low.toLocaleString('en-US') + ' and ' + parsed.high.toLocaleString('en-US');
    return out;
};

tableView.actionPhrases = function(column) {
    var out = [];
    tableModel.table.actions.forEach(function(row) {
        var raw = tableModel.actionCell(column, row.target).trim();
        if (raw === '') { return; }
        out.push('set ' + shared.escape(tableModel.phraseFor(row.target)) + ' to ' + shared.escape(raw));
    });

    return out;
};

tableView.conditionPhrase = function(subject, parsed) {
    var phrase = shared.escape(tableModel.phraseFor(subject));

    if (parsed.kind === 'interval') { return phrase + ' is ' + this.formatIntervalPhrase(parsed); }
    if (parsed.kind === 'set') {
        var joined = shared.escape(parsed.items.join(', '));
        if (parsed.negated) { return phrase + ' is none of ' + joined; }
        if (parsed.items.length === 1) { return phrase + ' is ' + joined; }
        return phrase + ' is one of ' + joined;
    }
    if (parsed.kind === 'comparison') {
        return phrase + ' ' + tableModel.symbolPhrases[parsed.symbol] + ' ' + shared.escape(parsed.value);
    }

    var out = phrase + ' is ' + shared.escape(parsed.value);
    return out;
};

tableView.composeSentence = function(column) {
    var self = this;
    var keyword = function(text) { return '<span class="table-sentence-keyword">' + text + '</span>'; };

    if (column.number === 0) {
        var alwaysActions = this.actionPhrases(column);
        return keyword('Always') + ' ' + alwaysActions.join(' ' + keyword('and') + ' ') + '.';
    }

    var parts = [];
    tableModel.table.conditions.forEach(function(row) {
        var parsed = tableModel.parseCondition(column, row.letter);
        if (parsed.kind === 'any') { return; }
        parts.push(self.conditionPhrase(row.subject, parsed));
    });

    var actions = this.actionPhrases(column);
    var conditionPart = parts.length === 0 ? keyword('If') + ' anything matches' :
        keyword('If') + ' ' + parts.join(' ' + keyword('and') + ' ');
    var actionPart = actions.length === 0 ? 'do nothing yet, the actions are empty' :
        actions.join(' ' + keyword('and') + ' ');

    var out = conditionPart + ' ' + keyword('then') + ' ' + actionPart + '.';
    if (column.overrides.length > 0) {
        out += ' ' + keyword('This rule overrides rule ' + column.overrides[0] + '.');
    }

    return out;
};

tableView.renderSentence = function() {
    var bar = document.getElementById('table-sentence-bar');
    var column = this.selectedColumn === null ? undefined : tableModel.columnByLabel(this.selectedColumn);

    if (column === undefined) {
        bar.innerHTML = '<span class="table-sentence-tag">Rule reads</span>' +
            '<span class="table-sentence-text" style="color:var(--text4)">Click a column header to read the whole rule as a sentence.</span>';
        return;
    }

    var tag = column.number === 0 ? 'The Base rule reads' : 'Rule ' + shared.escape(this.selectedColumn) + ' reads';
    bar.innerHTML = '<span class="table-sentence-tag">' + tag + '</span>' +
        '<span class="table-sentence-text">' + this.composeSentence(column) + '</span>';
};

// ////////////////////////////////////////////////////////////////////////

})();
