// Demo config - the cards screen.
//
// One card per demo config set, each with a slider that applies itself the
// moment it is flipped, plus a master "Everything" slider above the grid.
// Each change only locks the sliders it touches, so several of them
// can move independently at the same time.
// Every card says below its header whether its set is imported and shows
// count pills linking to the screens its objects live on. While a change
// is on its way, an Importing or Removing badge shows by the sliders it
// touches, and once it is done, a green confirmation takes its place for a moment.
// The server answers each change with the details as they actually are
// afterwards, which is what the cards are repainted from, and the one
// "How does it work?" badge below the grid explains the page as a whole.

(function($) {

$(document).ready(function() {

// ////////////////////////////////////////////////////////////////////////

var config = {};

config.saveUrl = '/zato/demo-config/save';
config.cluster_id = '1';

// What a request that never reached its endpoint reports
config.applyErrorText = 'The change could not be applied';

// What a card says about its set below the header
config.statusOnLabel = 'Imported';
config.statusOffLabel = 'Not imported';

// What a change in flight says by the sliders it touches, one label per direction
config.runningImportLabel = 'Importing';
config.runningRemoveLabel = 'Removing';

// What a finished change confirms where its in-flight badge was, and for how long
config.okImportedLabel = 'OK, imported';
config.okRemovedLabel = 'OK, removed';
config.okVisibleMs = 1000;

// One card per demo config set, in the order they are rendered
config.sets = ['tutorial', 'hl7', 'scheduler', 'pubsub', 'kafka', 'ibm_mq'];

// What the page-wide help badge explains, anchored at the Everything slider
config.howItWorksText = 'Slide "Everything" to import or remove all demo config, ' +
    'or pick cards with demo config individually.';

// How each kind of object is called on a pill and where the pill points to -
// the cluster query parameter is appended when the link is built.
config.kinds = {
    'job':                 {one: 'job', many: 'jobs', url: '/zato/scheduler/', params: ''},
    'channel-rest':        {one: 'REST channel', many: 'REST channels', url: '/zato/http-soap/', params: '&connection=channel&transport=plain_http'},
    'outconn-rest':        {one: 'outgoing REST connection', many: 'outgoing REST connections', url: '/zato/http-soap/', params: '&connection=outgoing&transport=plain_http'},
    'sql':                 {one: 'SQL connection', many: 'SQL connections', url: '/zato/outgoing/sql/', params: ''},
    'security-apikey':     {one: 'API key', many: 'API keys', url: '/zato/security/apikey/', params: ''},
    'security-basic-auth': {one: 'Basic Auth definition', many: 'Basic Auth definitions', url: '/zato/security/basic-auth/', params: ''},
    'pubsub-topic':        {one: 'topic', many: 'topics', url: '/zato/pubsub/topic/', params: ''},
    'channel-ibm-mq':      {one: 'channel', many: 'channels', url: '/zato/channel/ibm-mq/', params: '&type_=channel-ibm-mq'},
    'outconn-ibm-mq':      {one: 'outgoing connection', many: 'outgoing connections', url: '/zato/outgoing/ibm-mq/', params: '&type_=outconn-ibm-mq'},
    'channel-kafka':       {one: 'channel', many: 'channels', url: '/zato/channel/kafka/', params: '&type_=channel-kafka'},
    'outconn-kafka':       {one: 'outgoing connection', many: 'outgoing connections', url: '/zato/outgoing/kafka/', params: '&type_=outconn-kafka'},
    'channel-hl7-mllp':    {one: 'MLLP channel', many: 'MLLP channels', url: '/zato/channel/hl7/mllp/', params: '&type_=channel-hl7-mllp'},
    'outconn-hl7-mllp':    {one: 'MLLP outgoing connection', many: 'MLLP outgoing connections', url: '/zato/outgoing/hl7/mllp/', params: '&type_=outconn-hl7-mllp'},
    'outconn-hl7-fhir':    {one: 'FHIR connection', many: 'FHIR connections', url: '/zato/outgoing/hl7/fhir/', params: ''}
};

// ////////////////////////////////////////////////////////////////////////

// What each set consists of and what exists, embedded by the server at render time
var dataElement = document.getElementById('demo-config-data');
var lastData = JSON.parse(dataElement.textContent);

var masterField = $('#id_demo_config_all');
var errorElement = document.getElementById('demo-config-error');

// ////////////////////////////////////////////////////////////////////////

var field = function(setName) {
    var out = $('#id_demo_config_' + setName);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

var renderCard = function(setName, setInfo) {

    field(setName).prop('checked', setInfo.is_present);

    var card = document.getElementById('demo-config-card-' + setName);
    card.classList.toggle('demo-config-set-off', !setInfo.is_present);

    // The line below the header says plainly whether the set is imported
    var status = document.getElementById('demo-config-status-' + setName);
    status.textContent = '';

    var statusBadge = document.createElement('span');

    if(setInfo.is_present) {
        statusBadge.className = 'dashboard-outcome-badge status-badge-on';
        statusBadge.textContent = config.statusOnLabel;
    }
    else {
        statusBadge.className = 'dashboard-outcome-badge status-badge-off';
        statusBadge.textContent = config.statusOffLabel;
    }

    status.appendChild(statusBadge);

    var body = document.getElementById('demo-config-body-' + setName);
    body.textContent = '';

    for(var groupIdx = 0; groupIdx < setInfo.groups.length; groupIdx++) {

        var group = setInfo.groups[groupIdx];
        var kindInfo = config.kinds[group.kind];

        // How many of this group's objects actually exist right now
        var existingCount = 0;

        for(var countIdx = 0; countIdx < group.items.length; countIdx++) {
            if(group.items[countIdx].exists) {
                existingCount++;
            }
        }

        var pill = document.createElement('a');
        pill.className = 'dashboard-pill demo-config-pill zato-link-unstyled';

        // A kind with nothing imported dims but still says how many objects
        // there would be, never a zero
        var shownCount = existingCount;

        if(existingCount === 0) {
            pill.className += ' demo-config-pill-empty';
            shownCount = group.items.length;
        }

        pill.href = kindInfo.url + '?cluster=' + config.cluster_id + kindInfo.params;

        var kindLabel = shownCount === 1 ? kindInfo.one : kindInfo.many;
        pill.textContent = shownCount + ' ' + kindLabel;

        body.appendChild(pill);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The master slider is on only when every set is
var syncMaster = function(data) {

    var allOn = true;

    for(var setIdx = 0; setIdx < config.sets.length; setIdx++) {
        var setName = config.sets[setIdx];
        if(!(setName in data) || !data[setName].is_present) {
            allOn = false;
        }
    }

    masterField.prop('checked', allOn);
};

// ////////////////////////////////////////////////////////////////////////

var renderAll = function(data) {

    for(var setIdx = 0; setIdx < config.sets.length; setIdx++) {

        var setName = config.sets[setIdx];

        // A view rendered while the server was unreachable embeds no details,
        // so a card without them is left as it stands
        if(setName in data) {
            renderCard(setName, data[setName]);
        }
    }

    syncMaster(data);
};

// ////////////////////////////////////////////////////////////////////////

// Which sets have a change on its way right now - each request only locks
// its own sliders, so the others stay free to move at the same time
var busySets = {};

var hasBusySets = function() {

    for(var setName in busySets) {
        if(busySets[setName]) {
            return true;
        }
    }

    return false;
};

// ////////////////////////////////////////////////////////////////////////

var markBusy = function(changedSets, isFromMaster) {

    for(var changedIdx = 0; changedIdx < changedSets.length; changedIdx++) {

        var setName = changedSets[changedIdx];
        busySets[setName] = true;

        field(setName).prop('disabled', true);

        var card = document.getElementById('demo-config-card-' + setName);
        card.classList.add('demo-config-busy');
    }

    // The master cannot flip everything while any set is still moving
    masterField.prop('disabled', true);

    // The master's own in-flight badge only shows for changes it started itself
    if(isFromMaster) {
        var master = document.getElementById('demo-config-master');
        master.classList.add('demo-config-busy');
    }
};

// ////////////////////////////////////////////////////////////////////////

var markDone = function(changedSets, isFromMaster) {

    for(var changedIdx = 0; changedIdx < changedSets.length; changedIdx++) {

        var setName = changedSets[changedIdx];
        delete busySets[setName];

        field(setName).prop('disabled', false);

        var card = document.getElementById('demo-config-card-' + setName);
        card.classList.remove('demo-config-busy');
    }

    if(isFromMaster) {
        var master = document.getElementById('demo-config-master');
        master.classList.remove('demo-config-busy');
    }

    // The master frees up once nothing is moving anywhere
    if(!hasBusySets()) {
        masterField.prop('disabled', false);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Each badge about to show says which way its slider just went
var setRunningLabels = function(desiredStates, changedSets, isFromMaster) {

    for(var changedIdx = 0; changedIdx < changedSets.length; changedIdx++) {

        var setName = changedSets[changedIdx];
        var labelText = desiredStates[setName] ? config.runningImportLabel : config.runningRemoveLabel;

        document.getElementById('demo-config-running-label-' + setName).textContent = labelText;
    }

    // A master-driven change moves every set the same way,
    // so its own badge reads like any of theirs
    if(isFromMaster) {
        var masterText = masterField.is(':checked') ? config.runningImportLabel : config.runningRemoveLabel;
        document.getElementById('demo-config-running-label-all').textContent = masterText;
    }
};

// ////////////////////////////////////////////////////////////////////////

// A finished change confirms itself where its in-flight badge was,
// then steps back out of the way on its own
var showOkBadge = function(element, text) {

    element.textContent = text;
    element.classList.add('demo-config-ok-visible');

    // A confirmation shown again before the last one faded keeps its full time
    clearTimeout(element._demoConfigOkTimer);

    element._demoConfigOkTimer = setTimeout(function() {
        element.classList.remove('demo-config-ok-visible');
    }, config.okVisibleMs);
};

// Only the confirmations of the sliders a new change touches step aside -
// the ones from other changes still running or just finished stay put
var hideOkBadges = function(changedSets, isFromMaster) {

    var elements = [];

    for(var changedIdx = 0; changedIdx < changedSets.length; changedIdx++) {
        elements.push(document.getElementById('demo-config-ok-' + changedSets[changedIdx]));
    }

    if(isFromMaster) {
        elements.push(document.getElementById('demo-config-ok-all'));
    }

    for(var elementIdx = 0; elementIdx < elements.length; elementIdx++) {
        var element = elements[elementIdx];
        clearTimeout(element._demoConfigOkTimer);
        element.classList.remove('demo-config-ok-visible');
    }
};

// ////////////////////////////////////////////////////////////////////////

// The endpoint answers with a message on success and an error on failure,
// the failure arriving as a 500 with the same JSON body.
var errorTextFromResponse = function(xhr, defaultText) {

    var out = defaultText;

    try {
        var response = JSON.parse(xhr.responseText);
        if(response.error) {
            out = response.error;
        }
        else if(response.message) {
            out = response.message;
        }
    }
    catch(ignored) {
        if(xhr.responseText) {
            out = xhr.responseText;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The request carries only the sets it changes, so several changes
// can be on their way at the same time without touching each other
var apply = function(desiredStates, changedSets, isFromMaster) {

    // Whatever the last change said is no longer about what is on screen
    errorElement.textContent = '';
    hideOkBadges(changedSets, isFromMaster);

    setRunningLabels(desiredStates, changedSets, isFromMaster);
    markBusy(changedSets, isFromMaster);

    $.ajax({
        url: config.saveUrl,
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            states: desiredStates
        }),
        contentType: 'application/json',
        success: function(response) {
            markDone(changedSets, isFromMaster);

            // Only this change's cards are repainted - the others may have
            // their own changes still on the way, so they are left alone
            for(var setIdx = 0; setIdx < changedSets.length; setIdx++) {
                var changedName = changedSets[setIdx];
                lastData[changedName] = response.sets[changedName];
                renderCard(changedName, lastData[changedName]);
            }

            syncMaster(lastData);

            // .. and each changed slider confirms what just happened
            var firstOkText = '';

            for(var changedIdx = 0; changedIdx < changedSets.length; changedIdx++) {

                var setName = changedSets[changedIdx];
                var action = response.results[setName].action;

                // The server saw no difference for this set, so there is nothing to confirm
                if(action === 'unchanged') {
                    continue;
                }

                var okText = action === 'imported' ? config.okImportedLabel : config.okRemovedLabel;
                showOkBadge(document.getElementById('demo-config-ok-' + setName), okText);

                if(!firstOkText) {
                    firstOkText = okText;
                }
            }

            // A master-driven change flips every set the same way,
            // so its own confirmation reads like any of theirs
            if(isFromMaster && firstOkText) {
                showOkBadge(document.getElementById('demo-config-ok-all'), firstOkText);
            }
        },
        error: function(xhr) {
            markDone(changedSets, isFromMaster);
            errorElement.textContent = errorTextFromResponse(xhr, config.applyErrorText);

            // Only this change's sliders go back to what is actually
            // in the cluster - the others are none of its business
            for(var setIdx = 0; setIdx < changedSets.length; setIdx++) {
                var changedName = changedSets[setIdx];
                if(changedName in lastData) {
                    renderCard(changedName, lastData[changedName]);
                }
            }

            syncMaster(lastData);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.each(config.sets, function(_ignored, setName) {
    field(setName).on('change', function() {

        // The request speaks only for this one slider
        var desiredStates = {};
        desiredStates[setName] = field(setName).is(':checked');

        apply(desiredStates, [setName], false);
    });
});

masterField.on('change', function() {

    var isOn = masterField.is(':checked');

    var desiredStates = {};
    var changedSets = [];

    for(var setIdx = 0; setIdx < config.sets.length; setIdx++) {

        var setName = config.sets[setIdx];

        // Only the sets whose state actually flips travel with the request
        if(setName in lastData && lastData[setName].is_present !== isOn) {
            desiredStates[setName] = isOn;
            changedSets.push(setName);
        }

        field(setName).prop('checked', isOn);
    }

    apply(desiredStates, changedSets, true);
});

// ////////////////////////////////////////////////////////////////////////

// Every card shows its own set's objects from the moment the page opens ..
renderAll(lastData);

// .. the page-wide help explains itself at the Everything slider ..
$.fn.zato.how_it_works.init({
    badgeId: 'demo-config-how-it-works',
    divId: '#demo-config',
    fieldSelector: '.demo-config-master',

    // The master row sits at the top of the page, so the one tooltip
    // goes below it, over the cards it talks about
    placement: 'bottom',
    descriptions: {
        'id_demo_config_all': config.howItWorksText
    }
});

// .. and the page is shown once it is fully filled in.
$.fn.zato.dashboard_kit.reveal();

// ////////////////////////////////////////////////////////////////////////

});

})(jQuery);
