// MCP gateway wizard - the Data masking popover.
//
// A floating popover near the top of the window, of one fixed size whatever
// it shows. On the left, a scrolling grid of cards - the custom fields first,
// then the industry sets - each with a switch and a preview of its fields.
// On the right, a pane showing the card last clicked. For a set, the pane
// lists every field with a switch of its own under one switching them all.
// For the custom fields, it is their editor under the switch masking them or
// not - switched off, the fields stay in the editor and are not masked. The
// search of masking-search.js heads the grid and narrows the cards, and the
// pane shows the fields it matches in every set until a card is clicked.
// Select all covers the fields the pane shows, and Show only active narrows it to
// the fields masked at the moment it is switched on. OK writes the
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
        maskedOnly: 'Show only active',
        enabled: 'Enabled',
        noMatches: 'No matching fields',
        of: ' of ',
        masked: ' masked',
        sets: ' sets',
        separator: ', '
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

// A field is masked when a picked set lists it and it is not excluded, whichever set's pane shows it.
popover.isMasked = function(fieldName) {

    var working = popover.working;

    if(maskingSets.holds(working.excluded, fieldName)) {
        return false;
    }

    var listing = maskingSets.setsListing(fieldName);

    for(var setIdx = 0; setIdx < listing.length; setIdx++) {
        if(popover.isPicked(listing[setIdx])) {
            return true;
        }
    }

    return false;
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

// Picks a set with every one of its fields, or lets it go. An exclusion is of a field, whichever sets list it,
// so letting a set go keeps the exclusions of the fields the other picked sets still list.
popover.setPicked = function(setName, isOn) {

    var working = popover.working;

    working.sets = maskingSets.subtract(working.sets, [setName]);

    if(isOn) {
        working.sets.push(setName);
        working.excluded = maskingSets.subtract(working.excluded, maskingSets.allFieldsOf(setName));
        return;
    }

    var stillListed = maskingSets.union(working.sets);
    working.excluded = maskingSets.subtract(working.excluded, maskingSets.subtract(working.excluded, stillListed));
};

// ////////////////////////////////////////////////////////////////////////

popover.setFieldMasked = function(setName, fieldName, isOn) {

    if(popover.isMasked(fieldName) !== isOn) {
        popover.toggleField(setName, fieldName);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Switches one field shown in a set's pane. A field no picked set lists picks the set with that field alone,
// the set's other fields keeping what they had, and a picked set left with no field is let go.
popover.toggleField = function(setName, fieldName) {

    var working = popover.working;

    if(popover.isMasked(fieldName)) {

        working.excluded.push(fieldName);

        var pickedSets = working.sets.slice();

        for(var setIdx = 0; setIdx < pickedSets.length; setIdx++) {
            if(popover.maskedCountOf(pickedSets[setIdx]) === 0) {
                popover.setPicked(pickedSets[setIdx], false);
            }
        }

        return;
    }

    working.excluded = maskingSets.subtract(working.excluded, [fieldName]);

    if(popover.isMasked(fieldName)) {
        return;
    }

    var otherFields = maskingSets.subtract(maskingSets.allFieldsOf(setName), [fieldName]);
    var unmaskedOthers = [];

    for(var fieldIdx = 0; fieldIdx < otherFields.length; fieldIdx++) {
        if(!popover.isMasked(otherFields[fieldIdx])) {
            unmaskedOthers.push(otherFields[fieldIdx]);
        }
    }

    working.sets.push(setName);
    working.excluded = maskingSets.merge(working.excluded, unmaskedOthers);
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

popover._syncSetCard = function(card, terms) {

    var setName = card.getAttribute('data-key');
    var isPicked = popover.isPicked(setName);

    var isOut = function(fieldName) {
        var out = isPicked && !popover.isMasked(fieldName);
        return out;
    };

    card.classList.toggle('mcp-masking-card-on', isPicked);
    card.querySelector('.mcp-masking-card-count').textContent = popover.setCountLabel(setName);
    popover._setSwitch(card, isPicked);

    popover.search.fillPreview(card.querySelector('.mcp-masking-card-preview'), maskingSets.allFieldsOf(setName),
        terms, popover.config.previewCount, isOut);
};

// ////////////////////////////////////////////////////////////////////////

popover._syncCustomCard = function(card, terms) {

    var working = popover.working;

    card.classList.toggle('mcp-masking-card-on', working.isCustomEnabled && working.customFields.length > 0);
    card.classList.toggle('mcp-masking-card-off', !working.isCustomEnabled);
    card.querySelector('.mcp-masking-card-count').textContent = wizard.dataMasking.countLabel(working.customFields.length);
    popover._setSwitch(card, working.isCustomEnabled);

    popover.search.fillPreview(card.querySelector('.mcp-masking-card-preview'), working.customFields,
        terms, popover.config.previewCount, null);
};

// ////////////////////////////////////////////////////////////////////////

// The top of the pane - its title, its count, the switch showing the masked fields alone unless isMaskedOnly is null,
// and the row with the switch for all of it.
popover._buildPaneTop = function(pane, titleText, controlText, isOn, isMaskedOnly) {

    var header = document.createElement('div');
    header.className = 'mcp-masking-pane-header';

    var title = document.createElement('span');
    title.className = 'mcp-masking-pane-title';
    title.textContent = titleText;

    var count = document.createElement('span');
    count.className = 'mcp-masking-pane-count';

    header.appendChild(title);
    header.appendChild(count);

    if(isMaskedOnly !== null) {

        var only = document.createElement('span');
        only.className = 'mcp-masking-pane-only';

        var onlyLabel = document.createElement('span');
        onlyLabel.textContent = popover.config.labels.maskedOnly;

        only.appendChild(popover._buildSwitch(isMaskedOnly));
        only.appendChild(onlyLabel);
        header.appendChild(only);
    }

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

popover._fillSetPane = function(pane, setName, isMaskedOnly) {

    var set = maskingSets.get(setName);

    var isAllMasked = popover.maskedCountOf(setName) === set.fields.length;
    popover._buildPaneTop(pane, set.label, popover.config.labels.selectAll, isAllMasked, isMaskedOnly);
    popover._buildFieldList(pane, set.fields, false);
};

// ////////////////////////////////////////////////////////////////////////

// Whether every field the search shows is masked, and there is at least one.
popover._isAllShownMasked = function(pane) {

    var shown = popover._shownFields(pane);

    for(var fieldIdx = 0; fieldIdx < shown.length; fieldIdx++) {
        if(!popover.isMasked(shown[fieldIdx])) {
            return false;
        }
    }

    var out = shown.length > 0;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover._syncFieldPane = function(pane, countText) {

    var fieldRows = pane.querySelectorAll('.mcp-masking-pane-field');

    pane.querySelector('.mcp-masking-pane-count').textContent = countText;
    popover._setSwitch(pane.querySelector('.mcp-masking-pane-control'), popover._isAllShownMasked(pane));

    for(var rowIdx = 0; rowIdx < fieldRows.length; rowIdx++) {
        var fieldName = fieldRows[rowIdx].getAttribute('data-field');
        popover._setSwitch(fieldRows[rowIdx], popover.isMasked(fieldName));
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

    // The card the pane shows, a set's name or customKey, the terms of the search,
    // and whether the pane shows the fields they match in every set instead
    var focusKey = maskingSets.all()[0].name;
    var terms = [];
    var isResults = false;

    // The masked-only view keeps the fields masked when it was last asked for, so a field switched off stays in sight
    var isMaskedOnly = false;
    var maskedOnlyFields = null;

    var takeMaskedOnly = function() {
        maskedOnlyFields = isMaskedOnly ? popover.search.maskedInPane(pane) : null;
    };

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

    var searchRow = popover.search.build(function(newTerms) {
        terms = newTerms;
        isResults = terms.length > 0;
        renderPane(false);
    });
    cards.appendChild(searchRow.element);

    var customCard = popover._buildCardFrame(config.customKey, labels.custom, working.isCustomEnabled);
    cards.appendChild(customCard);

    var sets = maskingSets.all();

    for(var setIdx = 0; setIdx < sets.length; setIdx++) {
        cards.appendChild(popover._buildCardFrame(sets[setIdx].name, sets[setIdx].label, popover.isPicked(sets[setIdx].name)));
    }

    var cardsEmpty = document.createElement('div');
    cardsEmpty.className = 'mcp-masking-cards-empty';
    cardsEmpty.textContent = labels.noMatches;
    cards.appendChild(cardsEmpty);

    var fieldsOf = function(key) {

        if(key === config.customKey) {
            return working.customFields;
        }

        var out = maskingSets.allFieldsOf(key);
        return out;
    };

    var syncAll = function() {

        var allCards = cards.querySelectorAll('.mcp-masking-card');
        var found = [];
        var foundSetCount = 0;

        for(var cardIdx = 0; cardIdx < allCards.length; cardIdx++) {

            var card = allCards[cardIdx];
            var key = card.getAttribute('data-key');
            var matched = popover.search.matching(fieldsOf(key), terms);

            card.classList.toggle('mcp-masking-card-focused', !isResults && key === focusKey);
            card.classList.toggle('mcp-masking-card-unmatched', terms.length > 0 && matched.length === 0);

            if(key === config.customKey) {
                popover._syncCustomCard(card, terms);
            }
            else {
                popover._syncSetCard(card, terms);

                if(matched.length > 0) {
                    foundSetCount++;
                }
            }

            found = maskingSets.merge(found, matched);
        }

        cardsEmpty.classList.toggle('mcp-masking-cards-empty-on', terms.length > 0 && found.length === 0);
        searchRow.setResult(terms.length === 0 ? '' : popover.search.resultText(found.length, foundSetCount), found.length === 0);

        if(isResults) {
            popover._applyFilter(pane, terms, maskedOnlyFields);
            popover._syncFieldPane(pane, popover.search.resultsCountLabel(pane));
        }
        else if(focusKey === config.customKey) {
            popover._syncCustomPane(pane);
        }
        else {
            popover._applyFilter(pane, terms, maskedOnlyFields);
            popover._syncFieldPane(pane, popover.setCountLabel(focusKey));
        }

        popover._syncTotal(total);
    };

    // The editor of the custom fields takes the cursor only when its card was clicked, never away from the search
    var renderPane = function(isClicked) {

        pane.textContent = '';

        if(isResults) {
            popover.search.fillResultsPane(pane, terms, isMaskedOnly);
            takeMaskedOnly();
            syncAll();
            return;
        }

        if(focusKey !== config.customKey) {
            popover._fillSetPane(pane, focusKey, isMaskedOnly);
            takeMaskedOnly();
            syncAll();
            return;
        }

        popover._buildPaneTop(pane, labels.custom, labels.enabled, working.isCustomEnabled, null);

        var editorHost = document.createElement('div');
        editorHost.className = 'mcp-masking-pane-editor';
        pane.appendChild(editorHost);

        var inputId = forms.inputId(config.customInputField);

        var editor = wizard.dataMasking.buildEditor(editorHost, inputId, working.customFields, config.customPlaceholder, function(fields) {
            working.customFields = fields;
            syncAll();
        });

        syncAll();

        if(isClicked) {
            editor.textarea.focus();
        }
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
        if(isResults || key !== focusKey) {
            focusKey = key;
            isResults = false;
            renderPane(true);
        }
    });

    // A field of the results switched on picks the first set listing it if no picked set lists it
    var paneSetOf = function(fieldName) {

        if(isResults) {
            return maskingSets.setsListing(fieldName)[0];
        }

        return focusKey;
    };

    // Select all takes the state of the fields now shown at once, without sliding into it
    $(pane).on('click', '.mcp-masking-pane-only', function() {
        isMaskedOnly = !isMaskedOnly;
        popover._setSwitch(this, isMaskedOnly);
        takeMaskedOnly();
        pane.classList.add('mcp-masking-pane-instant');
        syncAll();
        pane.getBoundingClientRect();
        pane.classList.remove('mcp-masking-pane-instant');
    });

    $(pane).on('click', '.mcp-masking-pane-row', function() {

        if(this.classList.contains('mcp-masking-pane-field')) {
            var fieldName = this.getAttribute('data-field');
            popover.toggleField(paneSetOf(fieldName), fieldName);
        }
        else if(!isResults && focusKey === config.customKey) {
            working.isCustomEnabled = !working.isCustomEnabled;
        }
        else {
            var shown = popover._shownFields(pane);
            var isOn = !popover._isAllShownMasked(pane);

            for(var fieldIdx = 0; fieldIdx < shown.length; fieldIdx++) {
                popover.setFieldMasked(paneSetOf(shown[fieldIdx]), shown[fieldIdx], isOn);
            }
        }

        syncAll();
    });

    renderPane(false);
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
