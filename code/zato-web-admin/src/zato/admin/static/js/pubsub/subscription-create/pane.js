// Pub/sub - the form creating a subscription, the pane of topics, the footer and the clicks.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var form = $.fn.zato.pubsub.subscription_create;
var config = form.config;
var labels = config.labels;

// ////////////////////////////////////////////////////////////////////////

form.buildPaneTop = function(pane, titleText) {

    var header = document.createElement('div');
    header.className = 'mcp-masking-pane-header';

    var title = document.createElement('span');
    title.className = 'mcp-masking-pane-title';
    title.textContent = titleText;

    var count = document.createElement('span');
    count.className = 'mcp-masking-pane-count';

    var only = document.createElement('span');
    only.className = 'mcp-masking-pane-only';

    var onlyLabel = document.createElement('span');
    onlyLabel.textContent = labels.activeOnly;

    only.appendChild(form.buildSwitch(form.view.isActiveOnly));
    only.appendChild(onlyLabel);

    header.appendChild(title);
    header.appendChild(count);
    header.appendChild(only);

    var control = document.createElement('div');
    control.className = 'mcp-masking-pane-row mcp-masking-pane-control';

    var controlLabel = document.createElement('span');
    controlLabel.textContent = labels.selectAll;

    control.appendChild(form.buildSwitch(false));
    control.appendChild(controlLabel);

    pane.appendChild(header);
    pane.appendChild(control);
};

// ////////////////////////////////////////////////////////////////////////

// A row with a switch for each topic, the search results naming the group of each.
form.buildTopicList = function(pane, topicList, isNamed) {

    var list = document.createElement('div');
    list.className = 'mcp-masking-pane-list';

    for(var topicIdx = 0; topicIdx < topicList.length; topicIdx++) {

        var topicName = topicList[topicIdx];

        var topicRow = document.createElement('div');
        topicRow.className = 'mcp-masking-pane-row mcp-masking-pane-field';
        topicRow.setAttribute('data-topic', topicName);

        var name = document.createElement('span');
        name.className = 'mcp-masking-pane-name mcp-masking-mono';
        name.textContent = topicName;

        topicRow.appendChild(form.buildSwitch(form.isSelected(topicName)));
        topicRow.appendChild(name);

        if(isNamed) {
            var group = document.createElement('span');
            group.className = 'mcp-masking-pane-shared';
            group.textContent = form.groupNameOf(topicName);
            topicRow.appendChild(group);
        }

        list.appendChild(topicRow);
    }

    var empty = document.createElement('div');
    empty.className = 'mcp-masking-pane-empty';
    empty.textContent = labels.noMatches;
    list.appendChild(empty);

    pane.appendChild(list);
};

// ////////////////////////////////////////////////////////////////////////

form.paneRows = function() {
    var out = form.elements.pane.querySelectorAll('.mcp-masking-pane-field');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.shownTopics = function() {

    var shownRows = form.elements.pane.querySelectorAll('.mcp-masking-pane-field:not(.mcp-masking-filtered-out)');
    var out = [];

    for(var rowIdx = 0; rowIdx < shownRows.length; rowIdx++) {
        out.push(shownRows[rowIdx].getAttribute('data-topic'));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The active-only view keeps the topics picked when it was switched on, so a topic switched off stays in sight.
form.takeActiveOnly = function() {

    var view = form.view;

    view.activeOnlyTopics = null;

    if(!view.isActiveOnly) {
        return;
    }

    var rows = form.paneRows();
    var kept = [];

    for(var rowIdx = 0; rowIdx < rows.length; rowIdx++) {

        var topicName = rows[rowIdx].getAttribute('data-topic');

        if(form.isSelected(topicName)) {
            kept.push(topicName);
        }
    }

    view.activeOnlyTopics = kept;
};

// ////////////////////////////////////////////////////////////////////////

form.buildPane = function() {

    var view = form.view;
    var pane = form.elements.pane;

    pane.textContent = '';

    if(view.isResults) {
        var found = form.matching(form.visibleTopics(), view.terms);
        form.buildPaneTop(pane, labels.results);
        form.buildTopicList(pane, found, true);
    }
    else if(view.focusGroup !== null) {
        form.buildPaneTop(pane, view.focusGroup);
        form.buildTopicList(pane, form.topicsOfGroup(view.focusGroup), false);
    }

    form.takeActiveOnly();
    form.syncAll();
};

// ////////////////////////////////////////////////////////////////////////

form.syncPane = function() {

    var view = form.view;
    var pane = form.elements.pane;
    var rows = form.paneRows();

    if(pane.querySelector('.mcp-masking-pane-list') === null) {
        return;
    }

    for(var rowIdx = 0; rowIdx < rows.length; rowIdx++) {

        var topicName = rows[rowIdx].getAttribute('data-topic');
        var isKept = view.activeOnlyTopics === null || form.holds(view.activeOnlyTopics, topicName);
        var isShown = form.matches(topicName, view.terms) && isKept;

        rows[rowIdx].classList.toggle('mcp-masking-filtered-out', !isShown);
        form.highlight(rows[rowIdx].querySelector('.mcp-masking-pane-name'), topicName, view.terms);
        form.setSwitch(rows[rowIdx], form.isSelected(topicName));
    }

    var shown = form.shownTopics();
    var selectedShownCount = form.selectedCountOf(shown);
    var isAllShownSelected = shown.length > 0 && selectedShownCount === shown.length;

    var countText = '';

    if(view.isResults) {
        countText = form.partLabel(selectedShownCount, shown.length);
    }
    else {
        var groupTopics = form.topicsOfGroup(view.focusGroup);
        countText = form.partLabel(form.selectedCountOf(groupTopics), groupTopics.length);
    }

    pane.querySelector('.mcp-masking-pane-count').textContent = countText;
    pane.querySelector('.mcp-masking-pane-empty').classList.toggle('mcp-masking-pane-empty-on', shown.length === 0);
    form.setSwitch(pane.querySelector('.mcp-masking-pane-control'), isAllShownSelected);
};

// ////////////////////////////////////////////////////////////////////////

form.syncFooter = function() {

    var selectedCount = form.state.topics.length;

    form.elements.total.textContent = selectedCount === 0 ? labels.noneSelected : form.countLabel(selectedCount);
};

// ////////////////////////////////////////////////////////////////////////

form.syncAll = function() {
    form.syncCards();
    form.syncPane();
    form.syncFooter();
};

// ////////////////////////////////////////////////////////////////////////

// The cards follow what the subscriber sees, and the pane keeps its group while the group is still there.
form.renderTopics = function() {

    var view = form.view;
    var groups = form.groups();
    var isFocusKept = false;

    form.keepVisibleTopics();
    form.buildCards();

    for(var groupIdx = 0; groupIdx < groups.length; groupIdx++) {
        if(groups[groupIdx].name === view.focusGroup) {
            isFocusKept = true;
        }
    }

    if(!isFocusKept) {
        view.focusGroup = groups.length > 0 ? groups[0].name : null;
    }

    form.buildPane();
};

// ////////////////////////////////////////////////////////////////////////

form.onCardClick = function(event) {

    var card = event.target.closest('.mcp-masking-card');
    var view = form.view;

    if(card === null) {
        return;
    }

    var groupName = card.getAttribute('data-key');

    // The switch of a card picks the whole group, or lets it go when all of it is picked ..
    if(event.target.closest('.mcp-masking-switch')) {

        var topics = form.topicsOfGroup(groupName);
        var isOn = form.selectedCountOf(topics) !== topics.length;

        for(var topicIdx = 0; topicIdx < topics.length; topicIdx++) {
            form.setSelected(topics[topicIdx], isOn);
        }

        form.syncAll();
        return;
    }

    // .. and the rest of the card shows the group in the pane.
    if(view.isResults || groupName !== view.focusGroup) {
        view.focusGroup = groupName;
        view.isResults = false;
        form.buildPane();
    }
};

// ////////////////////////////////////////////////////////////////////////

form.onPaneClick = function(event) {

    var view = form.view;
    var pane = form.elements.pane;
    var only = event.target.closest('.mcp-masking-pane-only');
    var row = event.target.closest('.mcp-masking-pane-row');

    // The switches of the pane take the state of the topics now shown at once, without sliding into it
    if(only !== null) {
        view.isActiveOnly = !view.isActiveOnly;
        form.setSwitch(only, view.isActiveOnly);
        form.takeActiveOnly();
        pane.classList.add('mcp-masking-pane-instant');
        form.syncAll();
        pane.getBoundingClientRect();
        pane.classList.remove('mcp-masking-pane-instant');
        return;
    }

    if(row === null) {
        return;
    }

    if(row.classList.contains('mcp-masking-pane-field')) {
        var topicName = row.getAttribute('data-topic');
        form.setSelected(topicName, !form.isSelected(topicName));
    }
    else {
        var shown = form.shownTopics();
        var isOn = form.selectedCountOf(shown) !== shown.length;

        for(var topicIdx = 0; topicIdx < shown.length; topicIdx++) {
            form.setSelected(shown[topicIdx], isOn);
        }
    }

    form.syncAll();
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
