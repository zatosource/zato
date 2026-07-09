
// Mapper kit - search, filters and tree operations.
// One search box covers both trees and the expression text of every
// mapping row, with match highlighting and arrow-key navigation that
// expands collapsed branches on its way to a hit. The filter buttons
// narrow both trees to mapped, unmapped, required or invalid fields,
// and the tree operations collapse everything or expand exactly the
// mapped branches.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.search = {};

// ////////////////////////////////////////////////////////////////////////

    var expandedGlyph = '\u25be';
    var collapsedGlyph = '\u25b8';

// ////////////////////////////////////////////////////////////////////////

    // Initializes the search, the filters and the tree operations.
    // searchConfig:
    //   store:              the artifact store
    //   input:              the search text input
    //   countDisplay:       the element showing 'n of m'
    //   previousButton:     steps to the previous match
    //   nextButton:         steps to the next match
    //   filtersContainer:   the element the filter buttons render into
    //   collapseAllButton:  collapses every branch of both trees
    //   expandMappedButton: expands exactly the branches with mappings
    //   sourceBody:         the source tree body
    //   targetBody:         the target tree body
    //   listContainer:      the mapping list container
    //   onLayoutChanged:    called whenever visibility or expansion
    //                       changed row positions, so lines redraw
    zato.mapper.search.init = function(searchConfig) {

        var store = searchConfig.store;
        var input = searchConfig.input;
        var countDisplay = searchConfig.countDisplay;

        var treeBodies = [searchConfig.sourceBody, searchConfig.targetBody];

        var query = '';
        var filterName = config.defaultTreeFilter;
        var matches = [];
        var currentIdx = 0;

// ////////////////////////////////////////////////////////////////////////
// Tree expansion - shared by search navigation and the tree operations.
// ////////////////////////////////////////////////////////////////////////

        function setItemCollapsed(item, isCollapsed) {

            $(item).toggleClass('mapper-tree-item-collapsed', isCollapsed);

            var toggle = item.querySelector(':scope > .mapper-tree-row > .mapper-tree-toggle');
            if (toggle !== null) {
                toggle.textContent = isCollapsed ? collapsedGlyph : expandedGlyph;
            }
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

        // The matching paths for the active filter on one side.
        function filterMatches(artifact, mappedPaths, side) {

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

            var bodyIdx;

            // No filter shows everything again.
            if (filterName === 'all') {
                for (bodyIdx = 0; bodyIdx < treeBodies.length; bodyIdx++) {
                    $(treeBodies[bodyIdx]).find('.mapper-filter-hidden').removeClass('mapper-filter-hidden');
                }
                return;
            }

            var artifact = store.getArtifact();
            var mappedPaths = mappedPathsOf(zato.mapper.connections.list(artifact));

            for (bodyIdx = 0; bodyIdx < treeBodies.length; bodyIdx++) {
                var side = config.sides[bodyIdx];
                var matching = filterMatches(artifact, mappedPaths, side);

                // A match keeps its ancestors visible, so the tree
                // still reads as a tree.
                var visible = {};
                for (var matchPath in matching) {
                    var segments = matchPath.split('.');
                    for (var segmentIdx = 1; segmentIdx <= segments.length; segmentIdx++) {
                        visible[segments.slice(0, segmentIdx).join('.')] = true;
                    }
                }

                var items = treeBodies[bodyIdx].querySelectorAll('.mapper-tree-item');
                for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
                    var item = items[itemIdx];
                    var isHidden = !visible[item.getAttribute('data-path')];
                    $(item).toggleClass('mapper-filter-hidden', isHidden);
                }
            }
        }

// ////////////////////////////////////////////////////////////////////////
// Search - field names on both trees plus the target and expression
// text of every mapping row.
// ////////////////////////////////////////////////////////////////////////

        function clearSearchClasses() {

            var containers = [searchConfig.sourceBody, searchConfig.targetBody, searchConfig.listContainer];

            for (var containerIdx = 0; containerIdx < containers.length; containerIdx++) {
                $(containers[containerIdx]).find('.mapper-search-match').removeClass('mapper-search-match');
                $(containers[containerIdx]).find('.mapper-search-current').removeClass('mapper-search-current');
            }
        }

// ////////////////////////////////////////////////////////////////////////

        function collectMatches() {

            var out = [];
            var loweredQuery = query.toLowerCase();

            // Tree fields match on their names ..
            for (var bodyIdx = 0; bodyIdx < treeBodies.length; bodyIdx++) {
                var side = config.sides[bodyIdx];
                var items = treeBodies[bodyIdx].querySelectorAll('.mapper-tree-item');

                for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
                    var item = items[itemIdx];

                    // A field the active filter hides cannot be a hit.
                    if (item.closest('.mapper-filter-hidden') !== null) {
                        continue;
                    }

                    var row = item.querySelector(':scope > .mapper-tree-row');
                    var name = row.querySelector('.mapper-tree-name').textContent;

                    if (name.toLowerCase().indexOf(loweredQuery) !== -1) {
                        out.push({element: row, item: item, label: side + ' tree: ' + item.getAttribute('data-path')});
                    }
                }
            }

            // .. mapping rows match on their whole visible text.
            var listRows = searchConfig.listContainer.querySelectorAll('.mapper-row');
            for (var rowIdx = 0; rowIdx < listRows.length; rowIdx++) {
                var listRow = listRows[rowIdx];

                if (listRow.textContent.toLowerCase().indexOf(loweredQuery) !== -1) {
                    var target = listRow.querySelector('.mapper-row-target').textContent;
                    var expression = listRow.querySelector('.mapper-row-expression').textContent;
                    out.push({element: listRow, item: null, label: 'mapping row: ' + target + ' \u2190 ' + expression});
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function matchLabels() {

            var out = [];
            for (var matchIdx = 0; matchIdx < matches.length; matchIdx++) {
                out.push(matches[matchIdx].label);
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function renderCount() {

            if (query === '') {
                countDisplay.textContent = '';
            }
            else if (matches.length === 0) {
                countDisplay.textContent = config.searchNoMatchesLabel;
            }
            else {
                countDisplay.textContent = (currentIdx + 1) + ' of ' + matches.length;
            }
        }

// ////////////////////////////////////////////////////////////////////////

        // Marks one match as current, expanding its branch and
        // scrolling it into view when asked to.
        function setCurrent(newIdx, scroll) {

            var previous = matches[currentIdx];
            if (previous !== undefined) {
                previous.element.classList.remove('mapper-search-current');
            }

            currentIdx = newIdx;

            var match = matches[currentIdx];
            match.element.classList.add('mapper-search-current');

            // A hit inside a collapsed branch expands its way there.
            if (match.item !== null) {
                expandAncestors(match.item);
            }

            if (scroll) {
                match.element.scrollIntoView({block: 'nearest'});
            }

            renderCount();
            searchConfig.onLayoutChanged();
        }

// ////////////////////////////////////////////////////////////////////////

        // Recomputes and re-highlights every match. A fresh search
        // starts at the first hit, a re-application after a re-render
        // keeps the position clamped in place.
        function applySearch(fresh) {

            clearSearchClasses();
            matches = [];

            if (query === '') {
                renderCount();
                return;
            }

            matches = collectMatches();

            // Every tree match expands its branch right away, so every
            // hit the counter reports is on screen, not folded away ..
            for (var expandIdx = 0; expandIdx < matches.length; expandIdx++) {
                if (matches[expandIdx].item !== null) {
                    expandAncestors(matches[expandIdx].item);
                    setItemCollapsed(matches[expandIdx].item, false);
                }
            }

            // .. and whatever still has no geometry - a row under an
            // inactive side tab - cannot be shown, so it is no match.
            var visibleMatches = [];
            for (var visibleIdx = 0; visibleIdx < matches.length; visibleIdx++) {
                if (matches[visibleIdx].element.offsetParent !== null) {
                    visibleMatches.push(matches[visibleIdx]);
                }
            }
            matches = visibleMatches;

            for (var matchIdx = 0; matchIdx < matches.length; matchIdx++) {
                matches[matchIdx].element.classList.add('mapper-search-match');
            }

            if (fresh) {
                zato.mapper.log('search', 'query results', {query: query, total: matches.length, matches: matchLabels()});
            }

            if (matches.length === 0) {
                renderCount();
                searchConfig.onLayoutChanged();
                return;
            }

            if (fresh) {
                currentIdx = 0;
            }
            if (currentIdx >= matches.length) {
                currentIdx = matches.length - 1;
            }

            setCurrent(currentIdx, fresh);
        }

// ////////////////////////////////////////////////////////////////////////

        function stepCurrent(direction) {

            if (matches.length === 0) {
                return;
            }

            var newIdx = (currentIdx + direction + matches.length) % matches.length;

            zato.mapper.log('search', 'match navigation', {query: query, index: newIdx + 1, total: matches.length, match: matches[newIdx].label});
            setCurrent(newIdx, true);
        }

// ////////////////////////////////////////////////////////////////////////
// Tree operations
// ////////////////////////////////////////////////////////////////////////

        function collapseAll() {

            for (var bodyIdx = 0; bodyIdx < treeBodies.length; bodyIdx++) {
                var items = treeBodies[bodyIdx].querySelectorAll('.mapper-tree-item');

                for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
                    var item = items[itemIdx];
                    if (item.querySelector(':scope > .mapper-tree-children') !== null) {
                        setItemCollapsed(item, true);
                    }
                }
            }

            zato.mapper.log('search', 'collapsed all branches', {});
            searchConfig.onLayoutChanged();
        }

// ////////////////////////////////////////////////////////////////////////

        // Collapses everything, then expands exactly the branches
        // holding mapped fields on either side.
        function expandMapped() {

            collapseAll();

            var mappedPaths = mappedPathsOf(zato.mapper.connections.list(store.getArtifact()));

            for (var bodyIdx = 0; bodyIdx < treeBodies.length; bodyIdx++) {
                var side = config.sides[bodyIdx];

                for (var mappedPath in mappedPaths[side]) {
                    var item = treeItemAt(treeBodies[bodyIdx], mappedPath);
                    if (item !== null) {
                        expandAncestors(item);
                    }
                }
            }

            zato.mapper.log('search', 'expanded the mapped branches', {});
            searchConfig.onLayoutChanged();
        }

// ////////////////////////////////////////////////////////////////////////
// Wiring
// ////////////////////////////////////////////////////////////////////////

        function buildFilterButtons() {

            for (var filterIdx = 0; filterIdx < config.treeFilters.length; filterIdx++) {
                var filter = config.treeFilters[filterIdx];

                var button = document.createElement('button');
                button.className = 'mapper-button zato-action-button mapper-filter-button';
                if (filter.name === filterName) {
                    button.className = 'mapper-button zato-action-button mapper-filter-button mapper-filter-button-active';
                }
                button.type = 'button';
                button.textContent = filter.label;
                button.setAttribute('data-filter', filter.name);

                searchConfig.filtersContainer.appendChild(button);
            }
        }

        buildFilterButtons();

// ////////////////////////////////////////////////////////////////////////

        $(searchConfig.filtersContainer).on('click', '.mapper-filter-button', function() {

            filterName = this.getAttribute('data-filter');

            zato.mapper.log('search', 'filter changed', {filter: filterName});

            $(searchConfig.filtersContainer).find('.mapper-filter-button-active').removeClass('mapper-filter-button-active');
            $(this).addClass('mapper-filter-button-active');

            applyFilter();
            applySearch(true);
            searchConfig.onLayoutChanged();
        });

// ////////////////////////////////////////////////////////////////////////

        $(input).on('input', function() {
            query = input.value.trim();
            applySearch(true);
        });

        // Enter and the vertical arrows move between matches while
        // the input keeps focus.
        $(input).on('keydown', function(event) {

            if (event.key === 'Enter' || event.key === 'ArrowDown') {
                event.preventDefault();
                stepCurrent(event.shiftKey && event.key === 'Enter' ? -1 : 1);
            }
            else if (event.key === 'ArrowUp') {
                event.preventDefault();
                stepCurrent(-1);
            }
        });

        $(searchConfig.nextButton).on('click', function() {
            stepCurrent(1);
        });

        $(searchConfig.previousButton).on('click', function() {
            stepCurrent(-1);
        });

        $(searchConfig.collapseAllButton).on('click', collapseAll);
        $(searchConfig.expandMappedButton).on('click', expandMapped);

// ////////////////////////////////////////////////////////////////////////

        // Store changes re-render the trees, wiping classes - the filter
        // and the highlights re-apply on top of the fresh DOM.
        store.subscribe(function() {
            applyFilter();
            applySearch(false);
        });

        // The mapping list also re-renders whenever preview results
        // arrive, outside any store notification - the observer puts
        // the row highlights back. Class changes are attribute
        // mutations, so watching child lists only can never loop.
        var observer = new MutationObserver(function() {
            if (query !== '') {
                applySearch(false);
            }
        });
        observer.observe(searchConfig.listContainer, {childList: true, subtree: true});

        applyFilter();
    };

})(jQuery);
