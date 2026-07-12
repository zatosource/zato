
// Mapper kit - auto-map by name.
// Suggests mappings between fields whose names match - exactly first,
// then normalized (case and separators ignored) - either across the
// whole schemas or scoped to one structure dropped onto another.
// Repeating nodes pair up into iteration scope suggestions with their
// matching children. Everything is a reviewable suggestion with
// per-item accept, nothing ever applies silently.

(function($) {

    zato.mapper.automap = {};

// ////////////////////////////////////////////////////////////////////////

    // Lowercase with the separators removed, so order_id, Order-ID
    // and orderId all meet in one form.
    zato.mapper.automap.normalizeName = function(name) {

        var out = name.toLowerCase().replace(/[_\-\s]/g, '');
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // First-in-tree-order lookup tables of fields by exact name and
    // by normalized name, for one list of candidate fields.
    function buildNameIndex(fields) {

        var exact = {};
        var normalized = {};

        for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            var field = fields[fieldIdx];

            if (exact[field.name] === undefined) {
                exact[field.name] = field;
            }

            var normalizedName = zato.mapper.automap.normalizeName(field.name);
            if (normalized[normalizedName] === undefined) {
                normalized[normalizedName] = field;
            }
        }

        var out = {exact: exact, normalized: normalized};
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // The matching field for a name - exact first, then normalized.
    // Returns {field, matchKind} or null.
    function matchByName(index, name) {

        if (index.exact[name] !== undefined) {
            return {field: index.exact[name], matchKind: 'exact name'};
        }

        var normalizedName = zato.mapper.automap.normalizeName(name);
        if (index.normalized[normalizedName] !== undefined) {
            return {field: index.normalized[normalizedName], matchKind: 'normalized name'};
        }

        return null;
    }

// ////////////////////////////////////////////////////////////////////////

    // The fields of one kind that sit outside any repeating node
    // within the base subtree - repeating content pairs up through
    // the array matching instead.
    function fieldsOutsideArrays(baseNode, fields, kind) {

        var out = [];

        for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            var field = fields[fieldIdx];

            if (field.node.kind !== kind) {
                continue;
            }
            if (zato.mapper.schema.nearestArrayAncestor(baseNode, field.path) !== '') {
                continue;
            }

            out.push(field);
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function absolutePath(basePath, relativePath) {

        var out = basePath === '' ? relativePath : basePath + '.' + relativePath;
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // The matching child suggestions between two repeating nodes -
    // unmapped element leaf fields of the target array matched against
    // the element leaf fields of the source array, paths relative to
    // the arrays themselves.
    function matchArrayChildren(sourceArrayNode, targetArrayNode, mappedChildTargets) {

        var sourceLeaves = fieldsOutsideArrays(sourceArrayNode, zato.mapper.schema.listFields(sourceArrayNode), 'leaf');
        var targetLeaves = fieldsOutsideArrays(targetArrayNode, zato.mapper.schema.listFields(targetArrayNode), 'leaf');
        var sourceIndex = buildNameIndex(sourceLeaves);

        var out = [];

        for (var leafIdx = 0; leafIdx < targetLeaves.length; leafIdx++) {
            var targetLeaf = targetLeaves[leafIdx];

            if (mappedChildTargets[targetLeaf.path]) {
                continue;
            }

            var match = matchByName(sourceIndex, targetLeaf.name);
            if (match !== null) {
                out.push({target: targetLeaf.path, source: match.field.path, matchKind: match.matchKind});
            }
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Computes the suggestions between two subtrees - '' for a whole
    // side, a dotted path for the structure a drop scoped the run to.
    // Returns [{kind: 'row', target, source, matchKind}] mixed with
    // {kind: 'scope', target, source, matchKind, children} and
    // {kind: 'scope-addition', scopeIndex, target, source, children}.
    zato.mapper.automap.suggest = function(artifact, sourceScopePath, targetScopePath) {

        var out = [];

        var sourceRoot = artifact.source_schema.root;
        var targetRoot = artifact.target_schema.root;
        if (sourceRoot === null || targetRoot === null) {
            return out;
        }

        var sourceBase = sourceScopePath === '' ? sourceRoot : zato.mapper.schema.nodeAtPath(sourceRoot, sourceScopePath);
        var targetBase = targetScopePath === '' ? targetRoot : zato.mapper.schema.nodeAtPath(targetRoot, targetScopePath);
        if (sourceBase === null || targetBase === null) {
            return out;
        }

        // Everything already mapped is off the table - auto-map only
        // ever fills gaps, it never touches existing rows.
        var mappedTargets = {};
        var connections = zato.mapper.connections.list(artifact);
        for (var connectionIdx = 0; connectionIdx < connections.length; connectionIdx++) {
            mappedTargets[connections[connectionIdx].target] = true;
        }

        var sourceFields = zato.mapper.schema.listFields(sourceBase);
        var targetFields = zato.mapper.schema.listFields(targetBase);

        // Plain fields match one-to-one by name ..
        var sourceLeafIndex = buildNameIndex(fieldsOutsideArrays(sourceBase, sourceFields, 'leaf'));
        var targetLeaves = fieldsOutsideArrays(targetBase, targetFields, 'leaf');

        for (var leafIdx = 0; leafIdx < targetLeaves.length; leafIdx++) {
            var targetLeaf = targetLeaves[leafIdx];
            var absoluteTarget = absolutePath(targetScopePath, targetLeaf.path);

            if (mappedTargets[absoluteTarget]) {
                continue;
            }

            var leafMatch = matchByName(sourceLeafIndex, targetLeaf.name);
            if (leafMatch !== null) {
                out.push({
                    kind: 'row',
                    target: absoluteTarget,
                    source: absolutePath(sourceScopePath, leafMatch.field.path),
                    matchKind: leafMatch.matchKind
                });
            }
        }

        // .. and repeating nodes pair up into iteration scopes with
        // their matching children mapped relatively.
        var sourceArrayIndex = buildNameIndex(fieldsOutsideArrays(sourceBase, sourceFields, 'array'));
        var targetArrays = fieldsOutsideArrays(targetBase, targetFields, 'array');

        for (var arrayIdx = 0; arrayIdx < targetArrays.length; arrayIdx++) {
            var targetArray = targetArrays[arrayIdx];
            var arrayMatch = matchByName(sourceArrayIndex, targetArray.name);
            if (arrayMatch === null) {
                continue;
            }

            var absoluteArrayTarget = absolutePath(targetScopePath, targetArray.path);
            var absoluteArraySource = absolutePath(sourceScopePath, arrayMatch.field.path);

            // The pair may already be an iteration scope - then only
            // its unmapped children are suggested, into that scope.
            var existingScopeIdx = -1;
            var mappedChildTargets = {};

            for (var scopeIdx = 0; scopeIdx < artifact.scopes.length; scopeIdx++) {
                var scope = artifact.scopes[scopeIdx];
                if (scope.source === absoluteArraySource && scope.target === absoluteArrayTarget) {
                    existingScopeIdx = scopeIdx;
                    for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                        mappedChildTargets[scope.mappings[childIdx].target] = true;
                    }
                    break;
                }
            }

            var children = matchArrayChildren(arrayMatch.field.node, targetArray.node, mappedChildTargets);

            if (existingScopeIdx === -1) {
                out.push({
                    kind: 'scope',
                    target: absoluteArrayTarget,
                    source: absoluteArraySource,
                    matchKind: arrayMatch.matchKind,
                    children: children
                });
            }
            else if (children.length > 0) {
                out.push({
                    kind: 'scope-addition',
                    scopeIndex: existingScopeIdx,
                    target: absoluteArrayTarget,
                    source: absoluteArraySource,
                    children: children
                });
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    function newSuggestedRow(target, expression) {

        var out = zato.mapper.store.newMapping();
        out.target = target;
        out.expression = expression;
        out.origin = 'automap';

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function buildChildItems(children) {

        var out = [];
        for (var childIdx = 0; childIdx < children.length; childIdx++) {
            var child = children[childIdx];
            out.push({
                label: child.source + ' \u2192 ' + child.target,
                note: child.matchKind,
                suggestion: child
            });
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Opens the suggestion review for two subtrees and applies what
    // the review accepts, in one undoable step.
    // automapConfig:
    //   store:       the artifact store
    //   sourceScope: '' for the whole source side, or a structure path
    //   targetScope: '' for the whole target side, or a structure path
    zato.mapper.automap.openReview = function(automapConfig) {

        var store = automapConfig.store;

        var suggestions = zato.mapper.automap.suggest(store.getArtifact(), automapConfig.sourceScope, automapConfig.targetScope);

        zato.mapper.log('automap', 'suggestions computed', {sourceScope: automapConfig.sourceScope, targetScope: automapConfig.targetScope, count: suggestions.length});

        var items = [];
        for (var suggestionIdx = 0; suggestionIdx < suggestions.length; suggestionIdx++) {
            var suggestion = suggestions[suggestionIdx];

            if (suggestion.kind === 'row') {
                items.push({
                    label: suggestion.source + ' \u2192 ' + suggestion.target,
                    note: suggestion.matchKind,
                    suggestion: suggestion
                });
            }
            else if (suggestion.kind === 'scope') {
                items.push({
                    label: 'each ' + suggestion.source + ' \u2192 ' + suggestion.target,
                    note: suggestion.matchKind,
                    children: buildChildItems(suggestion.children),
                    suggestion: suggestion
                });
            }
            else {
                items.push({
                    label: 'each ' + suggestion.source + ' \u2192 ' + suggestion.target,
                    note: 'existing iteration',
                    children: buildChildItems(suggestion.children),
                    suggestion: suggestion
                });
            }
        }

        var scopeLabel = automapConfig.targetScope === '' ? 'the whole schemas' : automapConfig.targetScope + ' from ' + automapConfig.sourceScope;

        zato.mapper.reviewDialog.open({
            title: 'Auto-map suggestions - ' + scopeLabel,
            intro: 'Fields whose names match, exactly or normalized. Accept the suggestions to keep - nothing applies without review.',
            emptyText: 'Nothing to suggest - every field with a matching name is already mapped.',
            okLabel: 'Apply selected',
            items: items,
            onAccept: function(reviewedItems) {

                var rows = [];
                var scopes = [];
                var scopeAdditions = [];

                for (var itemIdx = 0; itemIdx < reviewedItems.length; itemIdx++) {
                    var item = reviewedItems[itemIdx];
                    if (!item.checked) {
                        continue;
                    }

                    if (item.suggestion.kind === 'row') {
                        rows.push(newSuggestedRow(item.suggestion.target, item.suggestion.source));
                        continue;
                    }

                    // A scope arrives with its accepted children only.
                    var childRows = [];
                    for (var childIdx = 0; childIdx < item.children.length; childIdx++) {
                        var childItem = item.children[childIdx];
                        if (childItem.checked) {
                            childRows.push(newSuggestedRow(childItem.suggestion.target, childItem.suggestion.source));
                        }
                    }

                    if (item.suggestion.kind === 'scope') {
                        scopes.push({target: item.suggestion.target, source: item.suggestion.source, mappings: childRows});
                    }
                    else if (childRows.length > 0) {
                        scopeAdditions.push({scopeIndex: item.suggestion.scopeIndex, rows: childRows});
                    }
                }

                zato.mapper.log('automap', 'applying accepted suggestions', {rows: rows.length, scopes: scopes.length, additions: scopeAdditions.length});

                if (rows.length > 0 || scopes.length > 0 || scopeAdditions.length > 0) {
                    store.applyAutoMap(rows, scopes, scopeAdditions);
                }
            }
        });
    };

})(jQuery);
