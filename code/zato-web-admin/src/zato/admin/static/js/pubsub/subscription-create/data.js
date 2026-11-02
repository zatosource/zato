// Pub/sub - the form creating a subscription, opened in the data table's create dialog.
// This file holds the data, the state and the helpers, render.js the subscriber's fields and the cards,
// subscriber.js the subscriber row, pane.js the pane of topics, the footer and the clicks,
// and dialog.js the data from the server, the dialog and the submission.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.namespace('zato.pubsub.subscription_create');

var form = $.fn.zato.pubsub.subscription_create;

// ////////////////////////////////////////////////////////////////////////

form.config = {

    idPrefix: 'pubsub-subscription-create-',

    dataURL: '/zato/pubsub/subscription/get-create-form-data/',

    // The data table's dialog the form opens in, and its width in pixels
    dialogId: '#create-div',
    dialogWidth: 1240,

    // The data table reads a checkbox of a new row by the id derived from its name
    activeInputId: 'id_is_delivery_active',
    activeInputName: 'is_delivery_active',

    // How many topics a card shows
    previewCount: 3,
    // How much wider than its longest option a select of the subscriber row is, in pixels
    selectExtraWidth: 24,

    kindService: 'service',
    kindClient: 'client',

    deliveryPull: 'pull',
    deliveryPush: 'push',

    pushTypeREST: 'rest',
    pushTypeService: 'service',

    // The first segment of a topic name names the card the topic belongs to
    segmentSeparators: /[._]/,

    labels: {
        title: 'Create a new pub/sub subscription',
        subscriber: 'Subscriber',
        active: 'Active',
        service: 'Service',
        client: 'API client',
        delivery: 'Delivery',
        pull: 'Pull',
        push: 'REST push',
        endpoint: 'REST endpoint',
        searchPlaceholder: 'Search topics',
        results: 'Search results',
        selectAll: 'Select all',
        activeOnly: 'Show only active',
        noMatches: 'No matching topics',
        noTopics: 'No topics',
        noClient: 'No API client selected',
        noneSelected: 'No topics selected',
        topic: ' topic',
        topics: ' topics',
        of: ' of ',
        within: ' in ',
        group: ' group',
        groups: ' groups',
        more: ' more'
    },

    icons: {
        search: '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
        clear: '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'
    }
};

// ////////////////////////////////////////////////////////////////////////

// The topics of each client and the name of each endpoint are keyed by the ID a select gives as its value.
form.takeData = function(data) {

    data.clientTopics = {};
    data.endpointNames = {};

    for(var clientIdx = 0; clientIdx < data.clients.length; clientIdx++) {
        var client = data.clients[clientIdx];
        data.clientTopics[client.id] = client.topics;
    }

    for(var endpointIdx = 0; endpointIdx < data.endpoints.length; endpointIdx++) {
        var endpoint = data.endpoints[endpointIdx];
        data.endpointNames[endpoint.id] = endpoint.name;
    }

    form.data = data;
};

// ////////////////////////////////////////////////////////////////////////

// The answers of a form just opened.
form.newState = function() {

    var out = {
        kind: form.config.kindService,
        service: '',
        client: '',
        delivery: form.config.deliveryPull,
        endpoint: '',
        isActive: true,
        topics: []
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The card the pane shows, the terms of the search, whether the pane shows what the search found,
// and the topics the active-only view keeps, null when it is off.
form.newView = function() {

    var out = {
        focusGroup: null,
        terms: [],
        isResults: false,
        isActiveOnly: false,
        activeOnlyTopics: null
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.state = form.newState();
form.view = form.newView();
form.elements = {};

// ////////////////////////////////////////////////////////////////////////

form.holds = function(list, item) {
    var out = list.indexOf(item) !== -1;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every topic for a service, the topics its permissions cover for a client.
form.visibleTopics = function() {

    var state = form.state;
    var out = [];

    if(state.kind === form.config.kindService) {
        out = form.data.topics;
    }
    else if(state.client !== '') {
        out = form.data.clientTopics[state.client];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.groupNameOf = function(topicName) {
    var out = topicName.split(form.config.segmentSeparators)[0];
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.groups = function() {

    var topics = form.visibleTopics();
    var byName = {};
    var out = [];

    for(var topicIdx = 0; topicIdx < topics.length; topicIdx++) {

        var topicName = topics[topicIdx];
        var groupName = form.groupNameOf(topicName);

        if(!(groupName in byName)) {
            byName[groupName] = {name: groupName, topics: []};
            out.push(byName[groupName]);
        }

        byName[groupName].topics.push(topicName);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.topicsOfGroup = function(groupName) {

    var groups = form.groups();

    for(var groupIdx = 0; groupIdx < groups.length; groupIdx++) {
        if(groups[groupIdx].name === groupName) {
            return groups[groupIdx].topics;
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

form.isSelected = function(topicName) {
    var out = form.holds(form.state.topics, topicName);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.setSelected = function(topicName, isOn) {

    var state = form.state;
    var isSelected = form.isSelected(topicName);

    if(isOn && !isSelected) {
        state.topics.push(topicName);
    }

    if(!isOn && isSelected) {
        state.topics.splice(state.topics.indexOf(topicName), 1);
    }
};

// ////////////////////////////////////////////////////////////////////////

form.selectedCountOf = function(topicList) {

    var out = 0;

    for(var topicIdx = 0; topicIdx < topicList.length; topicIdx++) {
        if(form.isSelected(topicList[topicIdx])) {
            out++;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A topic picked earlier that the subscriber no longer sees is let go.
form.keepVisibleTopics = function() {

    var visible = form.visibleTopics();
    var kept = [];

    for(var topicIdx = 0; topicIdx < form.state.topics.length; topicIdx++) {

        var topicName = form.state.topics[topicIdx];

        if(form.holds(visible, topicName)) {
            kept.push(topicName);
        }
    }

    form.state.topics = kept;
};

// ////////////////////////////////////////////////////////////////////////

form.countLabel = function(topicCount) {

    var labels = form.config.labels;

    if(topicCount === 0) {
        return labels.noTopics;
    }

    var noun = topicCount === 1 ? labels.topic : labels.topics;

    var out = topicCount + noun;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// All of a list, or how much of it is picked once only some of it is.
form.partLabel = function(selectedCount, totalCount) {

    if(selectedCount === 0 || selectedCount === totalCount) {
        return form.countLabel(totalCount);
    }

    var out = selectedCount + form.config.labels.of + form.countLabel(totalCount).toLowerCase();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.icon = function(iconName) {

    var icon = document.createElement('span');
    icon.className = 'mcp-search-box-icon';
    icon.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" ' +
        'stroke-linecap="round" stroke-linejoin="round">' + form.config.icons[iconName] + '</svg>';

    var out = icon;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A switch is built in the state it shows, so it never slides into it as the form appears.
form.buildSwitch = function(isOn) {

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

form.setSwitch = function(container, isOn) {
    container.querySelector('.mcp-masking-switch').classList.toggle('mcp-masking-switch-on', isOn);
};

// ////////////////////////////////////////////////////////////////////////

// The words of a query, a space separating them.
form.terms = function(text) {

    var words = text.toLowerCase().split(' ');
    var out = [];

    for(var wordIdx = 0; wordIdx < words.length; wordIdx++) {
        if(words[wordIdx] !== '') {
            out.push(words[wordIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.matches = function(topicName, terms) {

    var nameLower = topicName.toLowerCase();

    for(var termIdx = 0; termIdx < terms.length; termIdx++) {
        if(nameLower.indexOf(terms[termIdx]) === -1) {
            return false;
        }
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

form.matching = function(topicList, terms) {

    var out = [];

    for(var topicIdx = 0; topicIdx < topicList.length; topicIdx++) {
        if(form.matches(topicList[topicIdx], terms)) {
            out.push(topicList[topicIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Writes a topic's name into the element, each run of characters a term covers marked.
form.highlight = function(element, topicName, terms) {

    var nameLower = topicName.toLowerCase();
    var covered = [];

    element.textContent = '';

    for(var charIdx = 0; charIdx < topicName.length; charIdx++) {
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

    while(runStart < topicName.length) {

        var runEnd = runStart;

        while(runEnd < topicName.length && covered[runEnd] === covered[runStart]) {
            runEnd++;
        }

        var runText = topicName.substring(runStart, runEnd);

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

})(jQuery);
