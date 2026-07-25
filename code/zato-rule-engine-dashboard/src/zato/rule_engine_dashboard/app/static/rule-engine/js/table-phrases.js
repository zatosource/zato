'use strict';

// The sentence bar of the decision table: one selected column read back
// as a near-natural sentence, spoken from the server's reading of every
// cell. Augments the tableView namespace from table-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

// A number reads with its thousands separators, anything else as it stands
tableView.readingValue = function(value) {
    if (typeof value === 'number') { return value.toLocaleString('en-US'); }

    var out = String(value);
    return out;
};

tableView.formatRangePhrase = function(reading) {
    var low = this.readingValue(reading.low);
    var high = this.readingValue(reading.high);

    if (low === high) { return low; }

    var out = 'between ' + low + ' and ' + high;
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

tableView.conditionPhrase = function(subject, reading) {
    var self = this;
    var phrase = shared.escape(tableModel.phraseFor(subject));

    if (reading.kind === 'range') { return phrase + ' is ' + shared.escape(this.formatRangePhrase(reading)); }

    if (reading.kind === 'set') {
        var texts = reading.items.map(function(item) { return self.readingValue(item); });
        var joined = shared.escape(texts.join(', '));
        if (reading.negated) { return phrase + ' is none of ' + joined; }
        if (texts.length === 1) { return phrase + ' is ' + joined; }
        return phrase + ' is one of ' + joined;
    }

    if (reading.kind === 'comparison') {
        return phrase + ' ' + tableModel.symbolPhrases[reading.symbol] + ' ' +
            shared.escape(this.readingValue(reading.value));
    }

    // Text the cell grammar does not read is spoken back as it was typed, so
    // the sentence says what the cell says while the problems panel says why
    var out = phrase + ' ' + shared.escape(reading.text);
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
        var reading = tableModel.reading(column, row.letter);
        if (reading.kind === 'any') { return; }
        parts.push(self.conditionPhrase(row.subject, reading));
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
