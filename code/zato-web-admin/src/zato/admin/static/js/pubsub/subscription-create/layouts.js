// Pub/sub - the form creating a subscription, the layout of a few topics - one toggle for each topic
// under the field's label - and the choice between it and the cards.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var form = $.fn.zato.pubsub.subscription_create;
var config = form.config;
var labels = config.labels;

// ////////////////////////////////////////////////////////////////////////

form.chooseLayout = function() {

    var isFew = form.data.topics.length <= config.toggleTopicsMax;

    form.layout = isFew ? config.layoutToggles : config.layoutCards;
    form.elements.root.setAttribute('data-layout', form.layout);
};

// ////////////////////////////////////////////////////////////////////////

// A subscriber that sees a single topic subscribes to it.
form.selectSoleTopic = function() {

    var visible = form.visibleTopics();

    if(visible.length === 1) {
        form.setSelected(visible[0], true);
    }
};

// ////////////////////////////////////////////////////////////////////////

form.renderTopics = function() {

    form.keepVisibleTopics();
    form.selectSoleTopic();

    if(form.layout === config.layoutCards) {
        form.renderCards();
    }
    else {
        form.renderToggles();
    }
};

// ////////////////////////////////////////////////////////////////////////

// The part of the form that shows the topics, the one a submission without any points to.
form.topicsArea = function() {

    var out = form.elements.topics;

    if(form.layout === config.layoutCards) {
        out = form.elements.cards;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.buildToggle = function(topicName) {

    var toggle = document.createElement('div');
    toggle.className = 'mcp-masking-card ' + config.idPrefix + 'toggle mcp-masking-mono';
    toggle.setAttribute('data-topic', topicName);
    toggle.textContent = topicName;

    var out = toggle;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the box says when the subscriber sees no topics - a client with none is given a link
// to its permissions in a new tab.
form.buildTogglesEmpty = function() {

    var state = form.state;

    var empty = document.createElement('div');
    empty.className = config.idPrefix + 'toggles-empty';

    if(state.kind === config.kindService) {
        empty.textContent = labels.noTopics;
    }
    else if(state.client === '') {
        empty.textContent = labels.noClient;
    }
    else {

        var clientName = form.data.clientNames[state.client];

        var text = document.createElement('span');
        text.textContent = labels.noMatchingTopics + clientName;

        var link = document.createElement('a');
        link.href = config.permissionsURL + encodeURIComponent(clientName);
        link.target = '_blank';
        link.textContent = labels.addPermissions;

        empty.appendChild(text);
        empty.appendChild(link);
    }

    var out = empty;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.renderToggles = function() {

    var container = form.elements.topics;
    var topics = form.visibleTopics();

    container.textContent = '';

    if(topics.length === 0) {
        container.appendChild(form.buildTogglesEmpty());
        return;
    }

    var toggles = document.createElement('div');
    toggles.className = config.idPrefix + 'toggles';

    for(var topicIdx = 0; topicIdx < topics.length; topicIdx++) {
        toggles.appendChild(form.buildToggle(topics[topicIdx]));
    }

    container.appendChild(toggles);
    form.syncToggles();
};

// ////////////////////////////////////////////////////////////////////////

form.syncToggles = function() {

    var toggles = form.elements.topics.querySelectorAll('[data-topic]');

    for(var toggleIdx = 0; toggleIdx < toggles.length; toggleIdx++) {
        var toggle = toggles[toggleIdx];
        toggle.classList.toggle('mcp-masking-card-on', form.isSelected(toggle.getAttribute('data-topic')));
    }
};

// ////////////////////////////////////////////////////////////////////////

form.onTopicsClick = function(event) {

    var toggle = event.target.closest('[data-topic]');

    if(toggle === null) {
        return;
    }

    var topicName = toggle.getAttribute('data-topic');

    form.setSelected(topicName, !form.isSelected(topicName));
    form.syncToggles();
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
