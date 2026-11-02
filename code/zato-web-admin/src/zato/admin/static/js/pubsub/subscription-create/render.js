// Pub/sub - the form creating a subscription, the subscriber's fields and the cards of topic groups.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var form = $.fn.zato.pubsub.subscription_create;
var config = form.config;
var labels = config.labels;

// ////////////////////////////////////////////////////////////////////////

// A labeled select bound to one key of the state.
form.buildSelectField = function(stateKey, labelText, options) {

    var inputId = config.idPrefix + stateKey;

    var field = document.createElement('div');
    field.className = 'micro-form-field ' + config.idPrefix + 'field-' + stateKey;

    var label = document.createElement('label');
    label.className = 'micro-form-label';
    label.setAttribute('for', inputId);
    label.textContent = labelText;

    // The data table turns a select whose id names a service into a Chosen widget unless it opts out
    var select = document.createElement('select');
    select.className = 'micro-form-select noChosen';
    select.id = inputId;
    select.setAttribute('data-key', stateKey);

    for(var optionIdx = 0; optionIdx < options.length; optionIdx++) {

        var option = document.createElement('option');
        option.value = options[optionIdx].value;
        option.textContent = options[optionIdx].label;

        select.appendChild(option);
    }

    select.value = form.state[stateKey];

    field.appendChild(label);
    field.appendChild(select);

    var out = field;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.itemsToOptions = function(itemList) {

    var out = [{value: '', label: ''}];

    for(var itemIdx = 0; itemIdx < itemList.length; itemIdx++) {
        out.push({value: itemList[itemIdx].id, label: itemList[itemIdx].name});
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A service needs nothing past its name, a client needs its security definition
// and the way its messages reach it.
form.buildSubscriberFields = function() {

    var state = form.state;

    var fields = document.createElement('div');
    fields.className = 'micro-form-row ' + config.idPrefix + 'fields';

    if(state.kind === config.kindService) {
        fields.appendChild(form.buildServicesField());
    }
    else {

        var deliveryOptions = [
            {value: config.deliveryPull, label: labels.pull},
            {value: config.deliveryPush, label: labels.push}
        ];

        var endpointField = form.buildSelectField('endpoint', labels.endpoint, form.itemsToOptions(form.data.endpoints));
        endpointField.querySelector('select').disabled = state.delivery !== config.deliveryPush;

        fields.appendChild(form.buildSelectField('client', labels.client, form.itemsToOptions(form.data.clients)));
        fields.appendChild(form.buildSelectField('delivery', labels.delivery, deliveryOptions));
        fields.appendChild(endpointField);
    }

    var out = fields;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.buildSearch = function() {

    var row = document.createElement('div');
    row.className = 'mcp-masking-search-row';

    var box = document.createElement('div');
    box.className = 'mcp-search-box';

    var sizer = document.createElement('span');
    sizer.className = 'mcp-search-box-sizer';
    sizer.setAttribute('data-fit', labels.searchPlaceholder);

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'mcp-search-box-input';
    input.id = config.idPrefix + 'search';
    input.placeholder = labels.searchPlaceholder;
    input.spellcheck = false;
    input.autocomplete = 'off';

    var result = document.createElement('span');
    result.className = 'mcp-search-box-result';

    var clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'mcp-search-box-clear';
    clear.appendChild(form.icon('clear'));

    sizer.appendChild(input);

    box.appendChild(form.icon('search'));
    box.appendChild(sizer);
    box.appendChild(result);
    box.appendChild(clear);
    row.appendChild(box);

    form.elements.searchRow = row;
    form.elements.searchInput = input;
    form.elements.searchSizer = sizer;
    form.elements.searchResult = result;

    var onInput = function() {
        form.fitSearch();
        form.view.terms = form.terms(input.value);
        form.view.isResults = form.view.terms.length > 0;
        form.buildPane();
    };

    input.addEventListener('input', onInput);

    // Enter stays with the box rather than submitting the dialog's form
    input.addEventListener('keydown', function(event) {
        if(event.key === 'Enter') {
            event.preventDefault();
        }
    });

    box.addEventListener('click', function() {
        input.focus();
    });

    clear.addEventListener('click', function(event) {
        event.stopPropagation();
        input.value = '';
        onInput();
        input.focus();
    });

    var out = row;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The sizer takes the width of the value typed, or of the placeholder while there is none.
form.fitSearch = function() {

    var input = form.elements.searchInput;
    var fitText = input.value === '' ? input.placeholder : input.value;

    form.elements.searchSizer.setAttribute('data-fit', fitText);
};

// ////////////////////////////////////////////////////////////////////////

form.buildCard = function(groupName) {

    var card = document.createElement('div');
    card.className = 'mcp-masking-card';
    card.setAttribute('data-key', groupName);

    var header = document.createElement('div');
    header.className = 'mcp-masking-card-header';

    var title = document.createElement('span');
    title.className = 'mcp-masking-card-title';
    title.textContent = groupName;

    var count = document.createElement('div');
    count.className = 'mcp-masking-card-count';

    var preview = document.createElement('div');
    preview.className = 'mcp-masking-card-preview';

    header.appendChild(title);
    header.appendChild(form.buildSwitch(form.selectedCountOf(form.topicsOfGroup(groupName)) > 0));

    card.appendChild(header);
    card.appendChild(count);
    card.appendChild(preview);

    var out = card;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.buildCards = function() {

    var cards = form.elements.cards;
    var previous = cards.querySelectorAll('.mcp-masking-card, .mcp-masking-cards-empty');

    for(var previousIdx = 0; previousIdx < previous.length; previousIdx++) {
        cards.removeChild(previous[previousIdx]);
    }

    var groups = form.groups();

    for(var groupIdx = 0; groupIdx < groups.length; groupIdx++) {
        cards.appendChild(form.buildCard(groups[groupIdx].name));
    }

    var empty = document.createElement('div');
    empty.className = 'mcp-masking-cards-empty';
    cards.appendChild(empty);

    form.elements.cardsEmpty = empty;
};

// ////////////////////////////////////////////////////////////////////////

// The first topics of a card, or the ones the terms match with how many more match.
form.fillPreview = function(preview, topicList, terms, isOut) {

    var shownFrom = terms.length === 0 ? topicList : form.matching(topicList, terms);
    var shownCount = Math.min(shownFrom.length, config.previewCount);

    preview.textContent = '';

    for(var topicIdx = 0; topicIdx < shownCount; topicIdx++) {

        var topicName = shownFrom[topicIdx];

        var line = document.createElement('div');
        line.className = 'mcp-masking-card-line mcp-masking-mono';
        form.highlight(line, topicName, terms);
        line.classList.toggle('mcp-masking-line-out', isOut(topicName));

        preview.appendChild(line);
    }

    var restCount = shownFrom.length - shownCount;

    if(restCount > 0) {
        var more = document.createElement('div');
        more.className = 'mcp-masking-card-more';
        more.textContent = restCount + labels.more;
        preview.appendChild(more);
    }
};

// ////////////////////////////////////////////////////////////////////////

form.syncCards = function() {

    var view = form.view;
    var terms = view.terms;
    var allCards = form.elements.cards.querySelectorAll('.mcp-masking-card');
    var isFocusShown = !view.isResults && allCards.length > 1;
    var foundCount = 0;
    var foundGroupCount = 0;

    for(var cardIdx = 0; cardIdx < allCards.length; cardIdx++) {

        var card = allCards[cardIdx];
        var groupName = card.getAttribute('data-key');
        var topics = form.topicsOfGroup(groupName);
        var matched = form.matching(topics, terms);
        var selectedCount = form.selectedCountOf(topics);
        var isPicked = selectedCount > 0;

        var isOut = function(topicName) {
            var out = isPicked && !form.isSelected(topicName);
            return out;
        };

        card.classList.toggle('mcp-masking-card-on', isPicked);
        card.classList.toggle('mcp-masking-card-focused', isFocusShown && groupName === view.focusGroup);
        card.classList.toggle('mcp-masking-card-unmatched', terms.length > 0 && matched.length === 0);
        card.querySelector('.mcp-masking-card-count').textContent = form.partLabel(selectedCount, topics.length);
        form.setSwitch(card, isPicked);

        form.fillPreview(card.querySelector('.mcp-masking-card-preview'), topics, terms, isOut);

        foundCount += matched.length;

        if(matched.length > 0) {
            foundGroupCount++;
        }
    }

    var isNoneFound = terms.length > 0 && foundCount === 0;
    var isNoneAtAll = allCards.length === 0;
    var empty = form.elements.cardsEmpty;

    var isNoClient = form.state.kind === config.kindClient && form.state.client === '';
    var emptyText = labels.noMatches;

    if(isNoClient) {
        emptyText = labels.noClient;
    }
    else if(isNoneAtAll) {
        emptyText = labels.noTopics;
    }

    empty.textContent = emptyText;
    empty.classList.toggle('mcp-masking-cards-empty-on', isNoneAtAll || isNoneFound);
    form.elements.searchRow.hidden = isNoneAtAll;

    var resultText = '';

    if(terms.length > 0) {
        resultText = form.countLabel(foundCount);

        if(foundGroupCount > 0) {
            resultText += labels.within + foundGroupCount + (foundGroupCount === 1 ? labels.group : labels.groups);
        }
    }

    form.elements.searchResult.textContent = resultText;
    form.elements.searchResult.classList.toggle('mcp-search-box-result-none', isNoneFound);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
