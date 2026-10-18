// MCP gateway wizard - the search across the cards of the Data masking popover.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var maskingSets = wizard.maskingSets;
var popover = wizard.maskingPopover;
var search = {};

popover.search = search;

// ////////////////////////////////////////////////////////////////////////

search.config = {

    icons: {
        search: '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
        clear: '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'
    },

    labels: {
        placeholder: 'Search fields',
        results: 'Search results',
        clear: 'Clear',
        within: ' in ',
        set: ' set',
        sets: ' sets',
        more: ' more'
    }
};

// ////////////////////////////////////////////////////////////////////////

search._icon = function(iconName) {

    var icon = document.createElement('span');
    icon.className = 'mcp-search-box-icon';
    icon.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" ' +
        'stroke-linecap="round" stroke-linejoin="round">' + search.config.icons[iconName] + '</svg>';

    var out = icon;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The words of a query, a space and an underscore separating them alike.
search.terms = function(text) {

    var words = text.toLowerCase().replace(/_/g, ' ').split(' ');
    var out = [];

    for(var wordIdx = 0; wordIdx < words.length; wordIdx++) {
        if(words[wordIdx] !== '') {
            out.push(words[wordIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether a field's name holds every term, no terms matching every field.
search.matches = function(fieldName, terms) {

    var nameLower = fieldName.toLowerCase();

    for(var termIdx = 0; termIdx < terms.length; termIdx++) {
        if(nameLower.indexOf(terms[termIdx]) === -1) {
            return false;
        }
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

search.matching = function(fieldList, terms) {

    var out = [];

    for(var fieldIdx = 0; fieldIdx < fieldList.length; fieldIdx++) {
        if(search.matches(fieldList[fieldIdx], terms)) {
            out.push(fieldList[fieldIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Writes a field's name into the element, each run of characters a term covers marked.
search.highlight = function(element, fieldName, terms) {

    var nameLower = fieldName.toLowerCase();
    var covered = [];

    element.textContent = '';

    for(var charIdx = 0; charIdx < fieldName.length; charIdx++) {
        covered.push(false);
    }

    for(var termIdx = 0; termIdx < terms.length; termIdx++) {

        var term = terms[termIdx];
        var position = nameLower.indexOf(term);

        while(position !== -1) {

            for(var coverIdx = position; coverIdx < position + term.length; coverIdx++) {
                covered[coverIdx] = true;
            }

            position = nameLower.indexOf(term, position + 1);
        }
    }

    var runStart = 0;

    while(runStart < fieldName.length) {

        var runEnd = runStart;

        while(runEnd < fieldName.length && covered[runEnd] === covered[runStart]) {
            runEnd++;
        }

        var runText = fieldName.substring(runStart, runEnd);

        if(covered[runStart]) {
            var mark = document.createElement('mark');
            mark.className = 'mcp-masking-match';
            mark.textContent = runText;
            element.appendChild(mark);
        }
        else {
            element.appendChild(document.createTextNode(runText));
        }

        runStart = runEnd;
    }
};

// ////////////////////////////////////////////////////////////////////////

// Fills a card's preview - its first fields, or the ones matching the terms with how many more match.
// The isOut function, or null, says which fields are struck through.
search.fillPreview = function(preview, fieldList, terms, previewCount, isOut) {

    var shownFrom = terms.length === 0 ? fieldList : search.matching(fieldList, terms);
    var shownCount = Math.min(shownFrom.length, previewCount);

    preview.textContent = '';

    for(var fieldIdx = 0; fieldIdx < shownCount; fieldIdx++) {

        var fieldName = shownFrom[fieldIdx];

        var line = document.createElement('div');
        line.className = 'mcp-masking-card-line mcp-masking-mono';
        search.highlight(line, fieldName, terms);

        if(isOut !== null && isOut(fieldName)) {
            line.classList.add('mcp-masking-line-out');
        }

        preview.appendChild(line);
    }

    var restCount = shownFrom.length - shownCount;

    if(terms.length > 0 && restCount > 0) {
        var more = document.createElement('div');
        more.className = 'mcp-masking-card-more';
        more.textContent = restCount + search.config.labels.more;
        preview.appendChild(more);
    }
};

// ////////////////////////////////////////////////////////////////////////

// What the box says of the results - the fields found and in how many sets.
search.resultText = function(fieldCount, setCount) {

    var labels = search.config.labels;
    var out = wizard.dataMasking.countLabel(fieldCount);

    if(setCount > 0) {
        out += labels.within + setCount + (setCount === 1 ? labels.set : labels.sets);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Marks the rows the search does not show, or that onlyFields, unless null, does not list,
// each name shown with its matches marked, and says so when none is left.
popover._applyFilter = function(pane, terms, onlyFields) {

    var fieldRows = pane.querySelectorAll('.mcp-masking-pane-field');
    var shownCount = 0;

    for(var rowIdx = 0; rowIdx < fieldRows.length; rowIdx++) {

        var fieldName = fieldRows[rowIdx].getAttribute('data-field');
        var isShown = search.matches(fieldName, terms) && (onlyFields === null || maskingSets.holds(onlyFields, fieldName));

        fieldRows[rowIdx].classList.toggle('mcp-masking-filtered-out', !isShown);
        search.highlight(fieldRows[rowIdx].querySelector('.mcp-masking-pane-name'), fieldName, terms);

        if(isShown) {
            shownCount++;
        }
    }

    pane.querySelector('.mcp-masking-pane-empty').classList.toggle('mcp-masking-pane-empty-on', shownCount === 0);
};

// ////////////////////////////////////////////////////////////////////////

// The fields of the pane masked at this moment.
search.maskedInPane = function(pane) {

    var fieldRows = pane.querySelectorAll('.mcp-masking-pane-field');
    var out = [];

    for(var rowIdx = 0; rowIdx < fieldRows.length; rowIdx++) {

        var fieldName = fieldRows[rowIdx].getAttribute('data-field');

        if(popover.isMasked(fieldName)) {
            out.push(fieldName);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The fields the pane shows.
popover._shownFields = function(pane) {

    var fieldRows = pane.querySelectorAll('.mcp-masking-pane-field:not(.mcp-masking-filtered-out)');
    var out = [];

    for(var rowIdx = 0; rowIdx < fieldRows.length; rowIdx++) {
        out.push(fieldRows[rowIdx].getAttribute('data-field'));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A field listed by other sets too says by how many, the sets named in its title,
// and with isNamed, a field listed by one set names it.
popover._appendShared = function(fieldRow, fieldName, isNamed) {

    var labels = popover.config.labels;
    var setNames = maskingSets.setsListing(fieldName);

    if(setNames.length === 1 && !isNamed) {
        return;
    }

    var setLabels = [];

    for(var setIdx = 0; setIdx < setNames.length; setIdx++) {
        setLabels.push(maskingSets.get(setNames[setIdx]).label);
    }

    var shared = document.createElement('span');
    shared.className = 'mcp-masking-pane-shared';
    shared.textContent = setNames.length === 1 ? setLabels[0] : setNames.length + labels.sets;
    shared.title = setLabels.join(labels.separator);

    fieldRow.appendChild(shared);
};

// ////////////////////////////////////////////////////////////////////////

// The list of the pane - a row with a switch for each field and the line shown when the search leaves none.
popover._buildFieldList = function(pane, fieldNames, isNamed) {

    var list = document.createElement('div');
    list.className = 'mcp-masking-pane-list';

    for(var fieldIdx = 0; fieldIdx < fieldNames.length; fieldIdx++) {

        var fieldName = fieldNames[fieldIdx];

        var fieldRow = document.createElement('div');
        fieldRow.className = 'mcp-masking-pane-row mcp-masking-pane-field';
        fieldRow.setAttribute('data-field', fieldName);

        var name = document.createElement('span');
        name.className = 'mcp-masking-pane-name mcp-masking-mono';
        name.textContent = fieldName;

        fieldRow.appendChild(popover._buildSwitch(popover.isMasked(fieldName)));
        fieldRow.appendChild(name);
        popover._appendShared(fieldRow, fieldName, isNamed);
        list.appendChild(fieldRow);
    }

    var empty = document.createElement('div');
    empty.className = 'mcp-masking-pane-empty';
    empty.textContent = popover.config.labels.noMatches;
    list.appendChild(empty);

    pane.appendChild(list);
};

// ////////////////////////////////////////////////////////////////////////

// The pane of the results - every field of every set the terms match, each once, with the sets listing it.
search.fillResultsPane = function(pane, terms, isMaskedOnly) {

    var sets = maskingSets.all();
    var setNames = [];

    for(var setIdx = 0; setIdx < sets.length; setIdx++) {
        setNames.push(sets[setIdx].name);
    }

    var found = search.matching(maskingSets.union(setNames), terms);

    popover._buildPaneTop(pane, search.config.labels.results, popover.config.labels.selectAll, false, isMaskedOnly);
    popover._buildFieldList(pane, found, true);
};

// ////////////////////////////////////////////////////////////////////////

// What the pane of the results says of its size - all of it, or how much of it is masked.
search.resultsCountLabel = function(pane) {

    var dataMasking = wizard.dataMasking;
    var shown = popover._shownFields(pane);
    var maskedCount = 0;

    for(var fieldIdx = 0; fieldIdx < shown.length; fieldIdx++) {
        if(popover.isMasked(shown[fieldIdx])) {
            maskedCount++;
        }
    }

    if(maskedCount === shown.length) {
        return dataMasking.countLabel(shown.length);
    }

    var out = maskedCount + popover.config.labels.of + dataMasking.countLabel(shown.length).toLowerCase();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The search row heading the grid of cards - onChange receives the terms of every edit.
search.build = function(onChange) {

    var labels = search.config.labels;

    var row = document.createElement('div');
    row.className = 'mcp-masking-search-row';

    var box = document.createElement('div');
    box.className = 'mcp-search-box';

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'mcp-search-box-input';
    input.placeholder = labels.placeholder;
    input.spellcheck = false;
    input.autocomplete = 'off';

    var result = document.createElement('span');
    result.className = 'mcp-search-box-result';

    var clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'mcp-search-box-clear';
    clear.title = labels.clear;
    clear.appendChild(search._icon('clear'));

    box.appendChild(search._icon('search'));
    box.appendChild(input);
    box.appendChild(result);
    box.appendChild(clear);
    row.appendChild(box);

    wizard.searchBox.attach(box);

    // Enter stays with the box rather than accepting the popover, and Escape empties the box before it closes the popover
    input.addEventListener('keydown', function(event) {

        if(event.key === 'Enter') {
            event.preventDefault();
            event.stopPropagation();
        }

        if(event.key === 'Escape' && input.value !== '') {
            event.preventDefault();
            wizard.searchBox.clear(box);
        }
    });

    input.addEventListener('input', function() {
        onChange(search.terms(input.value));
    });

    var out = {
        element: row,
        setResult: function(text, isNone) {
            result.textContent = text;
            result.classList.toggle('mcp-search-box-result-none', isNone);
        }
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
