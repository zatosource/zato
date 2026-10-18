// MCP gateway wizard - the hook services of step 2.
//
// A hook service is one service the gateway invokes for every MCP request it
// receives, or for every MCP response it is about to return, independently
// of the services it exposes as tools. The Hook services line of step 2
// opens a popover with one decision line for each, whose chip opens a pick
// panel listing the deployed services, filtered by typing. The lines are
// moved into the popover and back to their holder on the step once it
// closes. The service names come from the Services source the page embeds
// for the Tools card.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var forms = wizard.forms;
var hooks = wizard.hooks;

// ////////////////////////////////////////////////////////////////////////

hooks.config = {

    // The popover the lines open in, and the link it opens from
    descriptorName: 'hooks',
    kindName: 'hookLines',
    title: 'Hook services',
    width: 520,
    editLinkId: 'mcp-wizard-edit-hooks',
    holderId: 'mcp-wizard-hooks-holder',
    bodyId: 'mcp-wizard-hooks-body',

    // Where the page embeds the tool sources, and the key of the one holding the services
    dataScriptId: 'mcp-wizard-tool-sources',
    servicesKey: 'services',

    // Where the page embeds the stored hook services, empty on create
    stateScriptId: 'mcp-wizard-masking-state',

    // The hooks in the order the lines show them, each with the slot its chip goes into
    kinds: ['request', 'response'],

    slots: {
        request: 'mcp-wizard-slot-request-hook',
        response: 'mcp-wizard-slot-response-hook'
    },

    titles: {
        request: 'Request',
        response: 'Response'
    },

    // The panel's starting width, how narrow its corners may drag it and the class lifting it over the popover
    panelWidth: 480,
    panelMinWidth: 340,
    panelClass: 'mcp-wizard-hook-panel',

    labels: {
        noService: 'No service',
        filter: 'Filter',
        filterServices: 'Filter services',
        services: 'Services',
        remove: 'Remove',
        noServices: 'No services',
        noMatches: 'No matching services'
    }
};

// ////////////////////////////////////////////////////////////////////////

// The deployed services and the one picked for each hook - an empty name
// is a hook with no service.
hooks.state = {
    serviceNames: [],
    request: '',
    response: ''
};

// ////////////////////////////////////////////////////////////////////////

hooks.init = function() {

    var config = hooks.config;

    var dataScript = document.getElementById(config.dataScriptId);
    var allNodes = JSON.parse(dataScript.textContent);

    // The Services source stands at the root of the tree, ahead of the connection groups
    for(var nodeIdx = 0; nodeIdx < allNodes.length; nodeIdx++) {
        var node = allNodes[nodeIdx];

        if(node.key === config.servicesKey) {
            hooks.state.serviceNames = node.items;
            break;
        }
    }

    var stateScript = document.getElementById(config.stateScriptId);
    var stored = JSON.parse(stateScript.textContent);

    hooks.state.request = stored.requestHook;
    hooks.state.response = stored.responseHook;

    hooks.render();

    $('#' + config.editLinkId).on('click', hooks.open);
};

// ////////////////////////////////////////////////////////////////////////

// Fills both lines with chips naming the service each hook invokes.
hooks.render = function() {

    var config = hooks.config;

    for(var kindIdx = 0; kindIdx < config.kinds.length; kindIdx++) {

        var kind = config.kinds[kindIdx];
        var serviceName = hooks.state[kind];
        var isBlank = serviceName === '';

        $.fn.zato.decision_lines.setChip(config.slots[kind], {
            text: isBlank ? config.labels.noService : serviceName,
            isBlank: isBlank,
            panel: {
                title: config.titles[kind],
                width: config.panelWidth,
                minWidth: config.panelMinWidth,
                panelClass: config.panelClass,
                build: hooks._panelBuilder(kind)
            }
        });
    }
};

// ////////////////////////////////////////////////////////////////////////

// The build function of one hook's panel - the filter, the heading and
// the list of services, the picked one marked.
hooks._panelBuilder = function(kind) {

    var out = function(body) {

        var lines = $.fn.zato.decision_lines;
        var labels = hooks.config.labels;

        var list = document.createElement('div');
        list.className = 'decision-pick-panel-list';

        var fill = function(filterText) {
            var picked = hooks._fillList(list, kind, filterText);
            return picked;
        };

        var filter = lines.buildFilter(labels.filter, labels.filterServices, fill);
        body.appendChild(filter.field);

        var heading = document.createElement('span');
        heading.className = 'micro-form-label';
        heading.textContent = labels.services;
        body.appendChild(heading);

        var picked = fill('');
        body.appendChild(list);

        // The list opens on the picked service, halfway down the view - the panel takes
        // its place and its remembered size right after this build, so the list has its
        // final height only in the next frame
        if(picked) {
            window.requestAnimationFrame(function() {
                list.scrollTop = picked.offsetTop - (list.clientHeight - picked.offsetHeight) / 2;
            });
        }

        var onClose = null;
        return onClose;
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Refills the list with the services the filter leaves and returns the row
// of the picked service, when the filter leaves it in.
hooks._fillList = function(list, kind, filterText) {

    var lines = $.fn.zato.decision_lines;
    var labels = hooks.config.labels;
    var serviceNames = hooks.state.serviceNames;
    var current = hooks.state[kind];

    var picked = null;
    var rowCount = 0;

    list.textContent = '';

    for(var nameIdx = 0; nameIdx < serviceNames.length; nameIdx++) {

        var name = serviceNames[nameIdx];
        var nameLower = name.toLowerCase();

        if(nameLower.indexOf(filterText) === -1) {
            continue;
        }

        var isPicked = name === current;
        var row = lines.buildPickRow(name, isPicked, hooks._picker(kind, name));

        list.appendChild(row);
        rowCount++;

        // Clicking the picked service is what leaves the hook without one
        if(isPicked) {
            var remove = document.createElement('span');
            remove.className = 'decision-pick-remove';
            remove.textContent = labels.remove;

            row.querySelector('.decision-pick-name').appendChild(remove);
            picked = row;
        }
    }

    if(rowCount === 0) {
        var empty = document.createElement('div');
        empty.className = 'decision-pick-panel-empty';
        empty.textContent = serviceNames.length ? labels.noMatches : labels.noServices;
        list.appendChild(empty);
    }

    return picked;
};

// ////////////////////////////////////////////////////////////////////////

// The click handler of one service's row in one hook's panel.
hooks._picker = function(kind, name) {

    var out = function() {

        if(hooks.state[kind] === name) {
            hooks.state[kind] = '';
        }
        else {
            hooks.state[kind] = name;
        }

        $.fn.zato.decision_lines.closePanel();
        hooks.render();
        wizard.review.refreshSummaries();
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the Hook services line says - the services picked, or that there are none.
hooks.summary = function() {

    var config = hooks.config;
    var names = [];

    for(var kindIdx = 0; kindIdx < config.kinds.length; kindIdx++) {
        if(hooks.state[config.kinds[kindIdx]] !== '') {
            names.push(hooks.state[config.kinds[kindIdx]]);
        }
    }

    if(names.length === 0) {
        return config.labels.noServices;
    }

    var out = names.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

hooks.open = function() {
    forms.open(hooks.config.descriptorName, document.getElementById(hooks.config.editLinkId));
};

// ////////////////////////////////////////////////////////////////////////

hooks._build = function(fieldSpec, row) {

    row.classList.add('micro-form-field-own');
    row.appendChild(document.getElementById(hooks.config.bodyId));
};

// ////////////////////////////////////////////////////////////////////////

// A pick panel opened from one of the lines closes with the popover, and the
// lines return to their holder on the step.
hooks._putAway = function() {

    var config = hooks.config;

    $.fn.zato.decision_lines.closePanel();
    document.getElementById(config.holderId).appendChild(document.getElementById(config.bodyId));
};

// ////////////////////////////////////////////////////////////////////////

// The review's edit link of the hook services - the step is already shown, the popover opens on it.
hooks.edit = function() {
    hooks.open();
};

// ////////////////////////////////////////////////////////////////////////

// The rows the review shows for the hook services.
hooks.reviewRows = function() {

    var config = hooks.config;
    var noneLabel = wizard.review.config.noneLabel;

    var out = [];

    for(var kindIdx = 0; kindIdx < config.kinds.length; kindIdx++) {

        var kind = config.kinds[kindIdx];
        var serviceName = hooks.state[kind];

        out.push([config.titles[kind], serviceName ? serviceName : noneLabel]);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The lines edit the state directly, which is why OK only closes the popover
forms.registerKind(hooks.config.kindName, {
    build: hooks._build,
    save: function() {}
});

forms.descriptors[hooks.config.descriptorName] = {
    title: hooks.config.title,
    width: hooks.config.width + 'px',
    pages: [[{kind: hooks.config.kindName}]],
    onClose: hooks._putAway
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
