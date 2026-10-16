// MCP gateway wizard - the Data masking popover.
//
// A floating popover near the top of the window, of one fixed size whatever
// it shows. On the left, a scrolling grid of cards - the custom fields first,
// then the industry sets - each with a switch and a preview of its fields.
// On the right, a pane showing the card last clicked. For a set, the pane
// lists every field with a switch of its own under one switching them all.
// For the custom fields, it is their editor under the switch masking them or
// not - switched off, the fields stay in the editor and are not masked. The
// list of a set has a filter over it, from masking-filters.js, and Select all
// covers the fields the filter shows. OK writes the
// working copy of the answers back to dataMasking.state.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var maskingSets = wizard.maskingSets;
var forms = wizard.forms;
var popover = wizard.maskingPopover;

// ////////////////////////////////////////////////////////////////////////

popover.config = {

    descriptorName: 'data_masking',
    kindName: 'maskingPopover',

    // The popover's width in pixels - its height is the stylesheet's
    width: 1200,

    // Where the popover opens the first time - this far from the top of the window,
    // centered across it and never closer than the margin to its left edge
    topOffset: 32,
    viewportMargin: 24,

    // How many fields a card shows
    previewCount: 3,

    // What the pane shows under, in place of a set's name, when it shows the custom fields
    customKey: 'custom',

    customInputField: 'data_masking_custom_fields',
    customPlaceholder: 'password\ncustomer.email\ncustomer.phone',

    labels: {
        title: 'Data masking',
        custom: 'Custom',
        selectAll: 'Select all',
        enabled: 'Enabled',
        noMatches: 'No matching fields',
        of: ' of ',
        masked: ' masked'
    }
};

// The answers the open popover edits
popover.working = null;

// ////////////////////////////////////////////////////////////////////////

popover.open = function(anchor) {
    forms.open(popover.config.descriptorName, anchor);
};

// ////////////////////////////////////////////////////////////////////////

popover._openPoint = function() {

    var config = popover.config;
    var centeredLeft = (window.innerWidth - config.width) / 2;

    var out = {
        left: Math.max(config.viewportMargin, centeredLeft),
        top: config.topOffset
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover._copyState = function(state) {

    var out = {
        sets: state.sets.slice(),
        excluded: state.excluded.slice(),
        customFields: state.customFields.slice(),
        isCustomEnabled: state.isCustomEnabled
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover.isPicked = function(setName) {
    var out = popover.working.sets.indexOf(setName) !== -1;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover.isMasked = function(setName, fieldName) {
    var out = popover.isPicked(setName) && popover.working.excluded.indexOf(fieldName) === -1;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover.maskedCountOf = function(setName) {

    if(!popover.isPicked(setName)) {
        return 0;
    }

    var kept = maskingSets.subtract(maskingSets.allFieldsOf(setName), popover.working.excluded);

    var out = kept.length;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Picks a set with every one of its fields, or lets it go.
popover.setPicked = function(setName, isOn) {

    var working = popover.working;

    working.sets = maskingSets.subtract(working.sets, [setName]);
    working.excluded = maskingSets.subtract(working.excluded, maskingSets.allFieldsOf(setName));

    if(isOn) {
        working.sets.push(setName);
    }
};

// ////////////////////////////////////////////////////////////////////////

popover.setFieldMasked = function(setName, fieldName, isOn) {

    if(popover.isMasked(setName, fieldName) !== isOn) {
        popover.toggleField(setName, fieldName);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Switches one field of a set. A field of a set not picked picks the set
// with that field alone, and a set left with no field is let go.
popover.toggleField = function(setName, fieldName) {

    var working = popover.working;
    var setFields = maskingSets.allFieldsOf(setName);

    if(!popover.isPicked(setName)) {
        popover.setPicked(setName, true);
        working.excluded = maskingSets.merge(working.excluded, maskingSets.subtract(setFields, [fieldName]));
        return;
    }

    if(popover.isMasked(setName, fieldName)) {
        working.excluded.push(fieldName);
    }
    else {
        working.excluded = maskingSets.subtract(working.excluded, [fieldName]);
    }

    if(popover.maskedCountOf(setName) === 0) {
        popover.setPicked(setName, false);
    }
};

// ////////////////////////////////////////////////////////////////////////

// What a set says of its size - all of it, or how much of it is masked once some is left out.
popover.setCountLabel = function(setName) {

    var dataMasking = wizard.dataMasking;
    var total = maskingSets.allFieldsOf(setName).length;
    var masked = popover.maskedCountOf(setName);

    if(!popover.isPicked(setName) || masked === total) {
        return dataMasking.countLabel(total);
    }

    var out = masked + popover.config.labels.of + dataMasking.countLabel(total).toLowerCase();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A switch is built in the state it shows, so it never slides into it as the popover appears.
popover._buildSwitch = function(isOn) {

    var switchElement = document.createElement('span');
    switchElement.className = 'mcp-masking-switch';
    switchElement.classList.toggle('mcp-masking-switch-on', isOn);

    var knob = document.createElement('span');
    knob.className = 'mcp-masking-switch-knob';

    switchElement.appendChild(knob);

    var out = switchElement;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover._setSwitch = function(container, isOn) {
    container.querySelector('.mcp-masking-switch').classList.toggle('mcp-masking-switch-on', isOn);
};

// ////////////////////////////////////////////////////////////////////////

// A card's frame - its title, its switch, a line for its count and one for its preview.
popover._buildCardFrame = function(key, titleText, isOn) {

    var card = document.createElement('div');
    card.className = 'mcp-masking-card';
    card.setAttribute('data-key', key);

    var header = document.createElement('div');
    header.className = 'mcp-masking-card-header';

    var title = document.createElement('span');
    title.className = 'mcp-masking-card-title';
    title.textContent = titleText;

    header.appendChild(title);
    header.appendChild(popover._buildSwitch(isOn));
    card.appendChild(header);

    var count = document.createElement('div');
    count.className = 'mcp-masking-card-count';
    card.appendChild(count);

    var preview = document.createElement('div');
    preview.className = 'mcp-masking-card-preview';
    card.appendChild(preview);

    var out = card;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover._buildSetCard = function(set) {

    var setFields = set.fields;

    var card = popover._buildCardFrame(set.name, set.label, popover.isPicked(set.name));
    var preview = card.querySelector('.mcp-masking-card-preview');

    for(var fieldIdx = 0; fieldIdx < popover.config.previewCount; fieldIdx++) {

        var line = document.createElement('div');
        line.className = 'mcp-masking-card-line mcp-masking-mono';
        line.setAttribute('data-field', setFields[fieldIdx]);
        line.textContent = setFields[fieldIdx];

        preview.appendChild(line);
    }

    var out = card;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover._syncSetCard = function(card) {

    var setName = card.getAttribute('data-key');
    var isPicked = popover.isPicked(setName);
    var lines = card.querySelectorAll('.mcp-masking-card-line');

    card.classList.toggle('mcp-masking-card-on', isPicked);
    card.querySelector('.mcp-masking-card-count').textContent = popover.setCountLabel(setName);
    popover._setSwitch(card, isPicked);

    for(var lineIdx = 0; lineIdx < lines.length; lineIdx++) {
        var isOut = isPicked && !popover.isMasked(setName, lines[lineIdx].getAttribute('data-field'));
        lines[lineIdx].classList.toggle('mcp-masking-line-out', isOut);
    }
};

// ////////////////////////////////////////////////////////////////////////

popover._syncCustomCard = function(card) {

    var working = popover.working;
    var preview = card.querySelector('.mcp-masking-card-preview');
    var shownCount = Math.min(working.customFields.length, popover.config.previewCount);

    card.classList.toggle('mcp-masking-card-on', working.isCustomEnabled && working.customFields.length > 0);
    card.classList.toggle('mcp-masking-card-off', !working.isCustomEnabled);
    card.querySelector('.mcp-masking-card-count').textContent = wizard.dataMasking.countLabel(working.customFields.length);
    popover._setSwitch(card, working.isCustomEnabled);

    preview.textContent = '';

    for(var fieldIdx = 0; fieldIdx < shownCount; fieldIdx++) {

        var line = document.createElement('div');
        line.className = 'mcp-masking-card-line mcp-masking-mono';
        line.textContent = working.customFields[fieldIdx];

        preview.appendChild(line);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The top of the pane - its title, its count and the row with the switch for all of it.
popover._buildPaneTop = function(pane, titleText, controlText, isOn) {

    var header = document.createElement('div');
    header.className = 'mcp-masking-pane-header';

    var title = document.createElement('span');
    title.className = 'mcp-masking-pane-title';
    title.textContent = titleText;

    var count = document.createElement('span');
    count.className = 'mcp-masking-pane-count';

    header.appendChild(title);
    header.appendChild(count);
    pane.appendChild(header);

    var control = document.createElement('div');
    control.className = 'mcp-masking-pane-row mcp-masking-pane-control';

    var controlLabel = document.createElement('span');
    controlLabel.textContent = controlText;

    control.appendChild(popover._buildSwitch(isOn));
    control.appendChild(controlLabel);
    pane.appendChild(control);
};

// ////////////////////////////////////////////////////////////////////////

popover._fillSetPane = function(pane, setName) {

    var set = maskingSets.get(setName);

    var isAllMasked = popover.maskedCountOf(setName) === set.fields.length;
    popover._buildPaneTop(pane, set.label, popover.config.labels.selectAll, isAllMasked);

    var list = document.createElement('div');
    list.className = 'mcp-masking-pane-list';

    for(var fieldIdx = 0; fieldIdx < set.fields.length; fieldIdx++) {

        var fieldRow = document.createElement('div');
        fieldRow.className = 'mcp-masking-pane-row mcp-masking-pane-field';
        fieldRow.setAttribute('data-field', set.fields[fieldIdx]);

        var name = document.createElement('span');
        name.className = 'mcp-masking-mono';
        name.textContent = set.fields[fieldIdx];

        fieldRow.appendChild(popover._buildSwitch(popover.isMasked(setName, set.fields[fieldIdx])));
        fieldRow.appendChild(name);
        list.appendChild(fieldRow);
    }

    var empty = document.createElement('div');
    empty.className = 'mcp-masking-pane-empty';
    empty.textContent = popover.config.labels.noMatches;
    list.appendChild(empty);

    pane.appendChild(list);
};

// ////////////////////////////////////////////////////////////////////////

// Marks the rows a filter does not show, null showing them all, and says so when none is left.
popover._applyFilter = function(pane, predicate) {

    var fieldRows = pane.querySelectorAll('.mcp-masking-pane-field');
    var shownCount = 0;

    for(var rowIdx = 0; rowIdx < fieldRows.length; rowIdx++) {

        var fieldName = fieldRows[rowIdx].getAttribute('data-field');
        var isShown = predicate === null || predicate(fieldName);

        fieldRows[rowIdx].classList.toggle('mcp-masking-filtered-out', !isShown);

        if(isShown) {
            shownCount++;
        }
    }

    pane.querySelector('.mcp-masking-pane-empty').classList.toggle('mcp-masking-pane-empty-on', shownCount === 0);
};

// ////////////////////////////////////////////////////////////////////////

// The fields of the set the filter shows.
popover._shownFields = function(pane) {

    var fieldRows = pane.querySelectorAll('.mcp-masking-pane-field:not(.mcp-masking-filtered-out)');
    var out = [];

    for(var rowIdx = 0; rowIdx < fieldRows.length; rowIdx++) {
        out.push(fieldRows[rowIdx].getAttribute('data-field'));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether every field the filter shows is masked, and there is at least one.
popover._isAllShownMasked = function(pane, setName) {

    var shown = popover._shownFields(pane);

    for(var fieldIdx = 0; fieldIdx < shown.length; fieldIdx++) {
        if(!popover.isMasked(setName, shown[fieldIdx])) {
            return false;
        }
    }

    var out = shown.length > 0;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover._syncSetPane = function(pane, setName) {

    var fieldRows = pane.querySelectorAll('.mcp-masking-pane-field');

    pane.querySelector('.mcp-masking-pane-count').textContent = popover.setCountLabel(setName);
    popover._setSwitch(pane.querySelector('.mcp-masking-pane-control'), popover._isAllShownMasked(pane, setName));

    for(var rowIdx = 0; rowIdx < fieldRows.length; rowIdx++) {
        var fieldName = fieldRows[rowIdx].getAttribute('data-field');
        popover._setSwitch(fieldRows[rowIdx], popover.isMasked(setName, fieldName));
    }
};

// ////////////////////////////////////////////////////////////////////////

popover._syncCustomPane = function(pane) {

    var working = popover.working;

    pane.querySelector('.mcp-masking-pane-count').textContent = wizard.dataMasking.countLabel(working.customFields.length);
    popover._setSwitch(pane.querySelector('.mcp-masking-pane-control'), working.isCustomEnabled);
};

// ////////////////////////////////////////////////////////////////////////

popover._syncTotal = function(total) {

    var dataMasking = wizard.dataMasking;
    var maskedCount = dataMasking.maskedFields(popover.working).length;

    var text = dataMasking.countLabel(maskedCount);

    if(maskedCount > 0) {
        text += popover.config.labels.masked;
    }

    total.textContent = text;
};

// ////////////////////////////////////////////////////////////////////////

popover.build = function(row) {

    var config = popover.config;
    var labels = config.labels;
    var working = popover.working;

    // The card the pane shows, a set's name or customKey
    var focusKey = maskingSets.all()[0].name;

    // What the filter of the pane's set shows - a function of a field's name, or null for every field
    var predicate = null;

    var layout = document.createElement('div');
    layout.className = 'mcp-masking-layout';
    row.appendChild(layout);

    var cards = document.createElement('div');
    cards.className = 'mcp-masking-cards';
    layout.appendChild(cards);

    var pane = document.createElement('div');
    pane.className = 'mcp-masking-pane';
    layout.appendChild(pane);

    var total = document.createElement('div');
    total.className = 'mcp-masking-total';
    row.appendChild(total);

    var customCard = popover._buildCardFrame(config.customKey, labels.custom, working.isCustomEnabled);
    cards.appendChild(customCard);

    var sets = maskingSets.all();

    for(var setIdx = 0; setIdx < sets.length; setIdx++) {
        cards.appendChild(popover._buildSetCard(sets[setIdx]));
    }

    var syncAll = function() {

        var setCards = cards.querySelectorAll('.mcp-masking-card');

        for(var cardIdx = 0; cardIdx < setCards.length; cardIdx++) {

            var card = setCards[cardIdx];
            card.classList.toggle('mcp-masking-card-focused', card.getAttribute('data-key') === focusKey);

            if(card !== customCard) {
                popover._syncSetCard(card);
            }
        }

        popover._syncCustomCard(customCard);

        if(focusKey === config.customKey) {
            popover._syncCustomPane(pane);
        }
        else {
            popover._applyFilter(pane, predicate);
            popover._syncSetPane(pane, focusKey);
        }

        popover._syncTotal(total);
    };

    var renderPane = function() {

        // Each set opens with its whole list, whatever the previous one was filtered by
        pane.textContent = '';
        predicate = null;

        if(focusKey !== config.customKey) {

            popover._fillSetPane(pane, focusKey);

            popover.filter({
                pane: pane,
                control: pane.querySelector('.mcp-masking-pane-control'),
                filter: function(newPredicate) {
                    predicate = newPredicate;
                    syncAll();
                }
            });

            syncAll();
            return;
        }

        popover._buildPaneTop(pane, labels.custom, labels.enabled, working.isCustomEnabled);

        var editorHost = document.createElement('div');
        editorHost.className = 'mcp-masking-pane-editor';
        pane.appendChild(editorHost);

        var inputId = forms.inputId(config.customInputField);

        var editor = wizard.dataMasking.buildEditor(editorHost, inputId, working.customFields, config.customPlaceholder, function(fields) {
            working.customFields = fields;
            syncAll();
        });

        editor.textarea.focus();
    };

    $(cards).on('click', '.mcp-masking-card', function(event) {

        var key = this.getAttribute('data-key');

        // The switch of a card is the whole of its set, or whether the custom fields are masked ..
        if(event.target.closest('.mcp-masking-switch')) {

            if(key === config.customKey) {
                working.isCustomEnabled = !working.isCustomEnabled;
            }
            else {
                popover.setPicked(key, !popover.isPicked(key));
            }

            syncAll();
            return;
        }

        // .. and the rest of the card shows it in the pane.
        if(key !== focusKey) {
            focusKey = key;
            renderPane();
        }
    });

    $(pane).on('click', '.mcp-masking-pane-row', function() {

        if(this.classList.contains('mcp-masking-pane-field')) {
            popover.toggleField(focusKey, this.getAttribute('data-field'));
        }
        else if(focusKey === config.customKey) {
            working.isCustomEnabled = !working.isCustomEnabled;
        }
        else {
            var shown = popover._shownFields(pane);
            var isOn = !popover._isAllShownMasked(pane, focusKey);

            for(var fieldIdx = 0; fieldIdx < shown.length; fieldIdx++) {
                popover.setFieldMasked(focusKey, shown[fieldIdx], isOn);
            }
        }

        syncAll();
    });

    renderPane();
};

// ////////////////////////////////////////////////////////////////////////

forms.descriptors[popover.config.descriptorName] = {
    title: popover.config.labels.title,
    width: popover.config.width + 'px',
    floating: true,
    openAt: popover._openPoint,
    pages: [[
        {field: popover.config.descriptorName, label: popover.config.labels.title, kind: popover.config.kindName}
    ]]
};

// ////////////////////////////////////////////////////////////////////////

forms.registerKind(popover.config.kindName, {

    build: function(fieldSpec, row) {
        popover.working = popover._copyState(wizard.dataMasking.state);
        row.classList.add('micro-form-field-own');
        popover.build(row);
    },

    save: function() {
        wizard.dataMasking.state = popover._copyState(popover.working);
    }
});

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
