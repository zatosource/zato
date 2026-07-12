
// Mapper kit - per-column search, filters and tree operations.
// Each column carries its own search box narrowing just its tree,
// and its own filter (picked from the column's menu) for mapped,
// unmapped, required or invalid fields. The per-side tree operations
// (collapse all, expand mapped) live in the same menu.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.search = {};

// ////////////////////////////////////////////////////////////////////////

    // Initializes the filters, the per-column search and the tree
    // operations.
    // searchConfig:
    //   store:              the artifact store
    //   sourceTreeInput:    the source column's own search box
    //   targetTreeInput:    the target column's own search box
    //   sourceBody:         the source tree body
    //   targetBody:         the target tree body
    //   onLayoutChanged:    called whenever visibility or expansion
    //                       changed row positions, so lines redraw
    // Returns {collapseTree, expandMappedTree, setFilter, getFilter},
    // each taking one side.
    zato.mapper.search.init = function(searchConfig) {

        var store = searchConfig.store;

        var treeBodies = [searchConfig.sourceBody, searchConfig.targetBody];

        var filterNames = {source: config.defaultTreeFilter, target: config.defaultTreeFilter};
        var treeQueries = {source: '', target: ''};

// ////////////////////////////////////////////////////////////////////////
// Tree expansion - shared by the tree operations.
// ////////////////////////////////////////////////////////////////////////

        // The collapsed class alone drives the chevron rotation, so no
        // glyph bookkeeping is needed here.
        function setItemCollapsed(item, isCollapsed) {
            $(item).toggleClass('mapper-tree-item-collapsed', isCollapsed);
        }

// ////////////////////////////////////////////////////////////////////////

        function expandAncestors(item) {

            var ancestor = item.parentElement.closest('.mapper-tree-item');
            while (ancestor !== null) {
                setItemCollapsed(ancestor, false);
                ancestor = ancestor.parentElement.closest('.mapper-tree-item');
            }
        }

// ////////////////////////////////////////////////////////////////////////

        function treeItemAt(body, path) {

            var out = body.querySelector('.mapper-tree-item[data-path="' + path + '"]');
            return out;
        }

// ////////////////////////////////////////////////////////////////////////
// Filters - each computes the set of matching paths per side, the
// trees then show the matches and their ancestors, nothing else.
// ////////////////////////////////////////////////////////////////////////

        // The absolute target paths already written by rows or scopes,
        // and the absolute source paths any expression references.
        function mappedPathsOf(connections) {

            var sources = {};
            var targets = {};

            for (var connectionIdx = 0; connectionIdx < connections.length; connectionIdx++) {
                var connection = connections[connectionIdx];

                for (var sourceIdx = 0; sourceIdx < connection.sources.length; sourceIdx++) {
                    sources[connection.sources[sourceIdx]] = true;
                }
                if (connection.target !== '') {
                    targets[connection.target] = true;
                }
            }

            var out = {source: sources, target: targets};
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function parses(text) {

            try {
                jsonata(text);
            } catch(error) {
                return false;
            }

            return true;
        }

// ////////////////////////////////////////////////////////////////////////

        // The target paths in an invalid state: required fields nothing
        // writes, and fields written by rows whose expression or
        // condition does not parse.
        function invalidTargetPaths(artifact, mappedTargets) {

            var out = {};

            // Required-but-unmapped leaves first ..
            var targetFields = zato.mapper.schema.listFields(artifact.target_schema.root);
            for (var fieldIdx = 0; fieldIdx < targetFields.length; fieldIdx++) {
                var field = targetFields[fieldIdx];
                if (field.node.kind === 'leaf' && !field.optional && !mappedTargets[field.path]) {
                    out[field.path] = true;
                }
            }

            // .. then the targets of rows that fail to parse.
            for (var rowIdx = 0; rowIdx < artifact.mappings.length; rowIdx++) {
                var row = artifact.mappings[rowIdx];
                if (row.expression !== '' && !parses(row.expression)) {
                    out[row.target] = true;
                }
                if (row.condition !== '' && !parses(row.condition)) {
                    out[row.target] = true;
                }
            }

            for (var scopeIdx = 0; scopeIdx < artifact.scopes.length; scopeIdx++) {
                var scope = artifact.scopes[scopeIdx];

                if (!parses(scope.source)) {
                    out[scope.target] = true;
                }

                for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                    var childRow = scope.mappings[childIdx];
                    var childTarget = scope.target + '.' + childRow.target;

                    if (childRow.expression !== '' && !parses(childRow.expression)) {
                        out[childTarget] = true;
                    }
                    if (childRow.condition !== '' && !parses(childRow.condition)) {
                        out[childTarget] = true;
                    }
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // The matching paths for one side's active filter.
        function filterMatches(artifact, mappedPaths, side) {

            var filterName = filterNames[side];

            var out = {};
            var root = artifact[side + '_schema'].root;

            // A side without a schema has no fields to filter.
            if (root === null) {
                return out;
            }

            if (filterName === 'mapped') {
                out = mappedPaths[side];
            }
            else if (filterName === 'unmapped') {
                var allPaths = zato.mapper.schema.listPaths(root);
                for (var pathIdx = 0; pathIdx < allPaths.length; pathIdx++) {
                    if (!mappedPaths[side][allPaths[pathIdx]]) {
                        out[allPaths[pathIdx]] = true;
                    }
                }
            }
            else if (filterName === 'required') {
                var fields = zato.mapper.schema.listFields(root);
                for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
                    if (!fields[fieldIdx].optional) {
                        out[fields[fieldIdx].path] = true;
                    }
                }
            }
            else if (filterName === 'invalid') {
                // Validity is a property of what writes the target side -
                // the source tree has no invalid fields of its own.
                if (side === 'target') {
                    out = invalidTargetPaths(artifact, mappedPaths.target);
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function applyFilter() {

            var artifact = store.getArtifact();
            var mappedPaths = mappedPathsOf(zato.mapper.connections.list(artifact));

            for (var bodyIdx = 0; bodyIdx < treeBodies.length; bodyIdx++) {
                var side = config.sides[bodyIdx];
                var body = treeBodies[bodyIdx];

                var filterActive = filterNames[side] !== 'all';
                var loweredTreeQuery = treeQueries[side].toLowerCase();
                var queryActive = loweredTreeQuery !== '';

                // Nothing narrows this side, so everything shows again.
                if (!filterActive && !queryActive) {
                    $(body).find('.mapper-filter-hidden').removeClass('mapper-filter-hidden');
                    continue;
                }

                var filterMatching = filterActive ? filterMatches(artifact, mappedPaths, side) : null;

                // A field stays when it passes both the filter and the
                // column's own search box.
                var items = body.querySelectorAll('.mapper-tree-item');
                var matching = {};
                var itemIdx;
                var item;

                for (itemIdx = 0; itemIdx < items.length; itemIdx++) {
                    item = items[itemIdx];
                    var path = item.getAttribute('data-path');

                    if (filterActive && !filterMatching[path]) {
                        continue;
                    }

                    if (queryActive) {
                        var name = item.querySelector(':scope > .mapper-tree-row .mapper-tree-name').textContent;
                        if (name.toLowerCase().indexOf(loweredTreeQuery) === -1) {
                            continue;
                        }
                    }

                    matching[path] = true;
                }

                // A match keeps its ancestors visible, so the tree
                // still reads as a tree.
                var visible = {};
                for (var matchPath in matching) {
                    var segments = matchPath.split('.');
                    for (var segmentIdx = 1; segmentIdx <= segments.length; segmentIdx++) {
                        visible[segments.slice(0, segmentIdx).join('.')] = true;
                    }
                }

                for (itemIdx = 0; itemIdx < items.length; itemIdx++) {
                    item = items[itemIdx];
                    var isHidden = !visible[item.getAttribute('data-path')];
                    $(item).toggleClass('mapper-filter-hidden', isHidden);
                }
            }
        }

// ////////////////////////////////////////////////////////////////////////
// Tree operations
// ////////////////////////////////////////////////////////////////////////

        var bodiesBySide = {source: searchConfig.sourceBody, target: searchConfig.targetBody};

        function collapseBody(body) {

            var items = body.querySelectorAll('.mapper-tree-item');

            for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
                var item = items[itemIdx];
                if (item.querySelector(':scope > .mapper-tree-children') !== null) {
                    setItemCollapsed(item, true);
                }
            }
        }

        function collapseTree(side) {

            collapseBody(bodiesBySide[side]);

            zato.mapper.log('search', 'collapsed one tree', {side: side});
            searchConfig.onLayoutChanged();
        }

// ////////////////////////////////////////////////////////////////////////

        // Expands exactly the branches holding mapped fields of one body,
        // everything else in it staying collapsed.
        function expandMappedBody(body, side) {

            collapseBody(body);

            var mappedPaths = mappedPathsOf(zato.mapper.connections.list(store.getArtifact()));

            for (var mappedPath in mappedPaths[side]) {
                var item = treeItemAt(body, mappedPath);
                if (item !== null) {
                    expandAncestors(item);
                }
            }
        }

        function expandMappedTree(side) {

            expandMappedBody(bodiesBySide[side], side);

            zato.mapper.log('search', 'expanded the mapped branches of one tree', {side: side});
            searchConfig.onLayoutChanged();
        }

// ////////////////////////////////////////////////////////////////////////
// Wiring
// ////////////////////////////////////////////////////////////////////////

        function setFilter(side, name) {

            filterNames[side] = name;

            zato.mapper.log('search', 'filter changed', {side: side, filter: name});

            applyFilter();
            searchConfig.onLayoutChanged();
        }

// ////////////////////////////////////////////////////////////////////////

        // Each column's own search box narrows just its tree, composing
        // with whatever filter that column has active.
        function wireTreeSearch(side, input) {

            $(input).on('input', function() {

                treeQueries[side] = input.value.trim();

                zato.mapper.log('search', 'tree query changed', {side: side, query: treeQueries[side]});

                applyFilter();
                searchConfig.onLayoutChanged();
            });
        }

        wireTreeSearch('source', searchConfig.sourceTreeInput);
        wireTreeSearch('target', searchConfig.targetTreeInput);

// ////////////////////////////////////////////////////////////////////////

        // Store changes re-render the trees, wiping classes - the filter
        // re-applies on top of the fresh DOM.
        store.subscribe(function() {
            applyFilter();
        });

        applyFilter();

        // The per-side tree operations and filters, used by the column
        // Options menus.
        return {
            collapseTree: collapseTree,
            expandMappedTree: expandMappedTree,
            setFilter: setFilter,
            getFilter: function(side) {
                return filterNames[side];
            }
        };
    };

})(jQuery);
