// MCP gateway wizard - the Tools card of step 1.
//
// One card serves every tool source - the services and each kind of
// outgoing connection. The sources stand in a tree whose group nodes
// mirror the dashboard menu, drawn with the dashboard kit's tree
// connectors. Clicking a leaf switches what the one badge picker on the
// right shows, and the picks of every source are kept while another one
// is on screen. The tree and its items come embedded in the page.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var toolSources = wizard.toolSources;

// ////////////////////////////////////////////////////////////////////////

toolSources.config = {

    // Where the page embeds the tree and its items
    dataScriptId: 'mcp-wizard-tool-sources',

    // The element the tree is built into
    listId: 'mcp-wizard-tool-source-list',

    // The action the shared badge picker is registered under
    pickerAction: 'wizard',

    // What the card summary says while nothing is assigned anywhere
    noneAssignedLabel: 'None assigned'
};

// ////////////////////////////////////////////////////////////////////////

// The card's state - the pruned tree, the leaves in their tree order, the
// picks each leaf holds while it is off screen and which leaf the picker
// currently shows.
toolSources.state = {
    tree: [],
    sources: [],
    assigned: {},
    activeKey: ''
};

// ////////////////////////////////////////////////////////////////////////

toolSources.init = function() {

    var state = toolSources.state;

    // The page embeds the whole tree ..
    var dataScript = document.getElementById(toolSources.config.dataScriptId);
    var allNodes = JSON.parse(dataScript.textContent);

    // .. a leaf with nothing to offer has no row and a group left without
    // leaves has none either - only what actually holds items appears ..
    state.tree = toolSources._prune(allNodes);

    // .. the leaves are collected in their tree order ..
    toolSources._collectLeaves(state.tree);

    // .. the tree is built ..
    toolSources._buildTree();

    // .. and the picker opens on the first leaf.
    toolSources.select(state.sources[0].key);
};

// ////////////////////////////////////////////////////////////////////////

// The given nodes without empty leaves, without groups that lost every
// child to the pruning, and with no single-child chains - a group left
// with exactly one child stands aside for that child.
toolSources._prune = function(nodes) {

    var out = [];

    for(var nodeIndex = 0; nodeIndex < nodes.length; nodeIndex++) {
        var node = nodes[nodeIndex];

        // A leaf carries a key, a group carries children ..
        if('key' in node) {
            if(node.items.length) {
                out.push(node);
            }
        } else {

            // .. a group with nothing left under it disappears ..
            var children = toolSources._prune(node.children);

            if(!children.length) {
                continue;
            }

            // .. a group with one child hands its place to that child ..
            if(children.length === 1) {
                out.push(children[0]);
            }

            // .. and any other group stays as it is.
            else {
                out.push({
                    label: node.label,
                    children: children
                });
            }
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Fills state.sources and state.assigned with the tree's leaves, in the
// order the tree draws them.
toolSources._collectLeaves = function(nodes) {

    var state = toolSources.state;

    for(var nodeIndex = 0; nodeIndex < nodes.length; nodeIndex++) {
        var node = nodes[nodeIndex];

        if('key' in node) {
            state.sources.push(node);

            // On edit the page embeds what the gateway already exposes,
            // on create every source starts with nothing picked.
            state.assigned[node.key] = node.assigned;
        } else {
            toolSources._collectLeaves(node.children);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

// One leaf's row - the label and, at the row's end, how many of its
// items are assigned.
toolSources._leafRow = function(node) {

    var row = document.createElement('div');
    row.className = 'mcp-tool-source';
    row.setAttribute('data-key', node.key);

    var label = document.createElement('span');
    label.className = 'mcp-tool-source-label';
    label.textContent = node.label;

    var count = document.createElement('span');
    count.className = 'mcp-tool-source-count';

    row.appendChild(label);
    row.appendChild(count);

    return row;
};

// ////////////////////////////////////////////////////////////////////////

// The given nodes rendered into a container - every node wears the kit's
// elbow, the roots included.
toolSources._buildNodes = function(nodes, container) {

    for(var nodeIndex = 0; nodeIndex < nodes.length; nodeIndex++) {
        var node = nodes[nodeIndex];

        var item = document.createElement('div');
        item.className = 'mcp-tool-node kit-tree-item';

        if('key' in node) {
            var row = toolSources._leafRow(node);
            item.appendChild(row);
        } else {

            var groupLabel = document.createElement('div');
            groupLabel.className = 'mcp-tool-group-label';
            groupLabel.textContent = node.label;

            var children = document.createElement('div');
            children.className = 'kit-tree-children';

            toolSources._buildNodes(node.children, children);

            item.appendChild(groupLabel);
            item.appendChild(children);
        }

        container.appendChild(item);
    }
};

// ////////////////////////////////////////////////////////////////////////

toolSources._buildTree = function() {

    var list = document.getElementById(toolSources.config.listId);

    toolSources._buildNodes(toolSources.state.tree, list);

    $(list).on('click', '.mcp-tool-source', function() {
        toolSources.select($(this).attr('data-key'));
    });
};

// ////////////////////////////////////////////////////////////////////////

// The leaf of the given key.
toolSources._source = function(key) {

    var sources = toolSources.state.sources;

    for(var sourceIndex = 0; sourceIndex < sources.length; sourceIndex++) {
        if(sources[sourceIndex].key === key) {
            var out = sources[sourceIndex];
            return out;
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

// What the picker's assigned zone holds right now - the badge text keeps
// the original case, unlike the lowercased data-name attribute.
toolSources._assignedInPicker = function() {

    var out = [];

    wizard.assignedBadges(toolSources.config.pickerAction).each(function() {
        out.push($(this).find('.security-badge-name').text());
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Saves the picks of the source currently on screen.
toolSources.storeActive = function() {

    var state = toolSources.state;

    if(state.activeKey) {
        state.assigned[state.activeKey] = toolSources._assignedInPicker();
    }
};

// ////////////////////////////////////////////////////////////////////////

toolSources.select = function(key) {

    var config = toolSources.config;
    var state = toolSources.state;

    // The picks of the source going off screen stay with it ..
    toolSources.storeActive();

    state.activeKey = key;

    // .. the row of the now current source is the marked one ..
    var rows = $('#' + config.listId + ' .mcp-tool-source');
    rows.removeClass('mcp-tool-source-active');
    rows.filter('[data-key="' + key + '"]').addClass('mcp-tool-source-active');

    // .. a filter typed for one source means nothing for another ..
    $('#badge-filter-text-' + config.pickerAction).val('');

    // .. and the picker reloads with the source's items, the ones picked
    // before opening in the assigned zone again.
    var source = toolSources._source(key);
    var assignedNames = state.assigned[key];
    var items = [];

    for(var itemIndex = 0; itemIndex < source.items.length; itemIndex++) {
        var name = source.items[itemIndex];
        items.push({
            id: name,
            name: name,
            is_member: assignedNames.indexOf(name) !== -1
        });
    }

    $.fn.zato.badge_picker.init(config.pickerAction, items, $.fn.zato.gateway.mcp.badge_picker_config);

    toolSources.syncCounts();
};

// ////////////////////////////////////////////////////////////////////////

// What one source holds right now - the one on screen is read from the
// picker itself, the others from the picks stored for them.
toolSources.assignedNames = function(key) {

    var state = toolSources.state;

    if(key === state.activeKey) {
        var out = toolSources._assignedInPicker();
        return out;
    }

    return state.assigned[key];
};

// ////////////////////////////////////////////////////////////////////////

// Brings every leaf row's count in line with what the leaf holds -
// a leaf with no picks says nothing.
toolSources.syncCounts = function() {

    var config = toolSources.config;
    var state = toolSources.state;

    for(var sourceIndex = 0; sourceIndex < state.sources.length; sourceIndex++) {

        var source = state.sources[sourceIndex];
        var assignedCount = toolSources.assignedNames(source.key).length;

        var row = $('#' + config.listId + ' .mcp-tool-source[data-key="' + source.key + '"]');
        row.find('.mcp-tool-source-count').text(assignedCount ? assignedCount : '');
    }
};

// ////////////////////////////////////////////////////////////////////////

// The card's one-line summary - what is assigned per source, e.g.
// "4 Services, 2 REST", or that nothing is assigned anywhere.
toolSources.summary = function() {

    var state = toolSources.state;
    var parts = [];

    for(var sourceIndex = 0; sourceIndex < state.sources.length; sourceIndex++) {

        var source = state.sources[sourceIndex];
        var assignedCount = toolSources.assignedNames(source.key).length;

        if(assignedCount) {
            parts.push(assignedCount + ' ' + source.full_label);
        }
    }

    if(!parts.length) {
        return toolSources.config.noneAssignedLabel;
    }

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every pick across every source, in tree order - the review and the
// save both read the picks grouped this way.
toolSources.allAssigned = function() {

    var state = toolSources.state;
    var out = [];

    for(var sourceIndex = 0; sourceIndex < state.sources.length; sourceIndex++) {

        var source = state.sources[sourceIndex];
        var names = toolSources.assignedNames(source.key);

        for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
            out.push({
                key: source.key,
                label: source.full_label,
                name: names[nameIndex]
            });
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
