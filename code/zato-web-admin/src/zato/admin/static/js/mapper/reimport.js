
// Mapper kit - schema re-import.
// Pasting a changed example next to an existing schema produces a diff
// review first: added, removed and renamed fields and type changes,
// each listing the mapping rows it affects, each with per-item accept.
// Nothing is destroyed silently - a mapping referencing a field whose
// removal was accepted stays in place and its unresolvable reference
// is a loud validation matter, never a quiet deletion.

(function($) {

    zato.mapper.reimport = {};

// ////////////////////////////////////////////////////////////////////////

    function typeLabelOf(node) {

        if (node.kind === 'object') {
            return 'object';
        }
        if (node.kind === 'array') {
            var elementLabel = typeLabelOf(node.element);
            return 'list of ' + elementLabel;
        }

        var out = node.types.join(' | ');
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function childPathOf(prefix, name) {

        var out = prefix === '' ? name : prefix + '.' + name;
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function diffFields(oldFields, newFields, prefix, changes) {

        var newByName = {};
        for (var newIdx = 0; newIdx < newFields.length; newIdx++) {
            newByName[newFields[newIdx].name] = newFields[newIdx];
        }

        var oldByName = {};
        for (var oldIdx = 0; oldIdx < oldFields.length; oldIdx++) {
            oldByName[oldFields[oldIdx].name] = oldFields[oldIdx];
        }

        // Fields gone from the new schema are removals, shared ones recurse ..
        for (var fieldIdx = 0; fieldIdx < oldFields.length; fieldIdx++) {
            var oldField = oldFields[fieldIdx];
            var path = childPathOf(prefix, oldField.name);

            var counterpart = newByName[oldField.name];
            if (counterpart === undefined) {
                changes.push({kind: 'removed', path: path, node: oldField.node, optional: oldField.optional});
            }
            else {
                diffNodes(oldField.node, counterpart.node, path, changes);
            }
        }

        // .. and fields only the new schema has are additions, whole subtrees.
        for (var addedIdx = 0; addedIdx < newFields.length; addedIdx++) {
            var newField = newFields[addedIdx];
            if (oldByName[newField.name] === undefined) {
                changes.push({kind: 'added', path: childPathOf(prefix, newField.name), node: newField.node});
            }
        }
    }

// ////////////////////////////////////////////////////////////////////////

    function diffNodes(oldNode, newNode, prefix, changes) {

        if (oldNode.kind === 'object' && newNode.kind === 'object') {
            diffFields(oldNode.fields, newNode.fields, prefix, changes);
            return;
        }

        // Array element fields share the array's path space, so two
        // arrays diff through their elements under the same prefix.
        if (oldNode.kind === 'array' && newNode.kind === 'array') {
            diffNodes(oldNode.element, newNode.element, prefix, changes);
            return;
        }

        // Everything else is a shape or type comparison at this node.
        var oldLabel = typeLabelOf(oldNode);
        var newLabel = typeLabelOf(newNode);

        if (oldLabel !== newLabel) {
            changes.push({kind: 'type-changed', path: prefix, from: oldLabel, to: newLabel, node: oldNode});
        }
    }

// ////////////////////////////////////////////////////////////////////////

    function parentPathOf(path) {

        var lastDot = path.lastIndexOf('.');
        if (lastDot === -1) {
            return '';
        }

        var out = path.substring(0, lastDot);
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function lastSegmentOf(path) {

        var lastDot = path.lastIndexOf('.');

        var out = lastDot === -1 ? path : path.substring(lastDot + 1);
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Turns removed-and-added pairs with identical subtrees under one
    // parent into rename changes, pairing them in tree order.
    function detectRenames(changes) {

        var out = [];
        var consumedAdditions = {};

        for (var changeIdx = 0; changeIdx < changes.length; changeIdx++) {
            var change = changes[changeIdx];

            if (change.kind !== 'removed') {
                out.push(change);
                continue;
            }

            // The first identical addition under the same parent is the
            // other half of a rename.
            var removedShape = JSON.stringify(change.node);
            var removedParent = parentPathOf(change.path);
            var renamed = false;

            for (var otherIdx = 0; otherIdx < changes.length; otherIdx++) {
                var other = changes[otherIdx];

                if (other.kind !== 'added' || consumedAdditions[otherIdx]) {
                    continue;
                }
                if (parentPathOf(other.path) !== removedParent) {
                    continue;
                }
                if (JSON.stringify(other.node) !== removedShape) {
                    continue;
                }

                consumedAdditions[otherIdx] = true;
                out.push({
                    kind: 'renamed',
                    path: change.path,
                    newName: lastSegmentOf(other.path),
                    newPath: other.path,
                    node: change.node
                });
                renamed = true;
                break;
            }

            if (!renamed) {
                out.push(change);
            }
        }

        // The additions consumed by renames drop out of the list.
        var final = [];
        for (var finalIdx = 0; finalIdx < out.length; finalIdx++) {
            var kept = out[finalIdx];
            if (kept.kind === 'added' && consumedAdditions[changes.indexOf(kept)]) {
                continue;
            }
            final.push(kept);
        }

        return final;
    }

// ////////////////////////////////////////////////////////////////////////

    // The full diff of two schema trees: added, removed and renamed
    // fields plus type changes, renames detected from identical
    // removed-and-added subtrees under one parent.
    zato.mapper.reimport.diff = function(oldRoot, newRoot) {

        var changes = [];
        diffNodes(oldRoot, newRoot, '', changes);

        var out = detectRenames(changes);
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The mapping rows a change at this path affects - references for
    // the source side, written targets for the target side.
    function affectedDetails(connections, side, path) {

        var out = [];

        for (var connectionIdx = 0; connectionIdx < connections.length; connectionIdx++) {
            var connection = connections[connectionIdx];

            if (side === 'source') {
                for (var sourceIdx = 0; sourceIdx < connection.sources.length; sourceIdx++) {
                    var source = connection.sources[sourceIdx];
                    if (source === path || source.indexOf(path + '.') === 0) {
                        out.push('Used by ' + connection.target);
                        break;
                    }
                }
            }
            else {
                if (connection.target === path || connection.target.indexOf(path + '.') === 0) {
                    out.push('Mapped: ' + connection.target + ' \u2190 ' + connection.sources.join(', '));
                }
            }
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // The mutable fields list of the node a path points at - the node's
    // own fields for an object, its element's for a repeating node.
    function fieldsAt(root, parentPath) {

        var node = parentPath === '' ? root : zato.mapper.schema.nodeAtPath(root, parentPath);
        if (node === null) {
            return null;
        }

        if (node.kind === 'object') {
            return node.fields;
        }
        if (node.kind === 'array' && node.element.kind === 'object') {
            return node.element.fields;
        }

        return null;
    }

// ////////////////////////////////////////////////////////////////////////

    // Builds the final tree from the new one by reverting every
    // unaccepted change, and collects the expression rewrites the
    // accepted renames cause.
    function applyReview(items, newRoot, mappings, scopes, side) {

        var root = zato.mapper.schema.clone(newRoot);

        for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
            var item = items[itemIdx];
            var change = item.change;

            // An accepted rename propagates into every reference ..
            if (change.kind === 'renamed' && item.checked) {
                var rewrites = zato.mapper.refactor.renameRewrites(mappings, scopes, side, change.path, change.newPath);
                zato.mapper.refactor.applyRewrites(mappings, scopes, rewrites);
                continue;
            }

            // .. everything else accepted is already part of the new tree.
            if (item.checked) {
                continue;
            }

            // Unaccepted changes revert one by one, keeping the old shape.
            if (change.kind === 'added') {
                var addedFields = fieldsAt(root, parentPathOf(change.path));
                var addedName = lastSegmentOf(change.path);
                for (var addedIdx = 0; addedIdx < addedFields.length; addedIdx++) {
                    if (addedFields[addedIdx].name === addedName) {
                        addedFields.splice(addedIdx, 1);
                        break;
                    }
                }
            }
            else if (change.kind === 'removed') {
                var removedFields = fieldsAt(root, parentPathOf(change.path));
                removedFields.push({
                    name: lastSegmentOf(change.path),
                    optional: change.optional,
                    node: zato.mapper.schema.clone(change.node)
                });
            }
            else if (change.kind === 'type-changed') {
                var typeFields = fieldsAt(root, parentPathOf(change.path));
                var typeName = lastSegmentOf(change.path);
                for (var typeIdx = 0; typeIdx < typeFields.length; typeIdx++) {
                    if (typeFields[typeIdx].name === typeName) {
                        typeFields[typeIdx].node = zato.mapper.schema.clone(change.node);
                        break;
                    }
                }
            }
            else {
                // An unaccepted rename keeps the old name on the new node.
                var renamedBack = zato.mapper.schema.renameField(root, change.newPath, lastSegmentOf(change.path));
                root = renamedBack.root;
            }
        }

        return root;
    }

// ////////////////////////////////////////////////////////////////////////

    function nextSampleName(artifact, side) {

        var count = 0;
        for (var sampleIdx = 0; sampleIdx < artifact.samples.length; sampleIdx++) {
            if (artifact.samples[sampleIdx].side === side) {
                count += 1;
            }
        }

        var out = side + '-reimport-' + (count + 1);
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function reviewItemOf(change, connections, side) {

        if (change.kind === 'added') {
            return {label: 'Added: ' + change.path, note: typeLabelOf(change.node), change: change};
        }

        if (change.kind === 'removed') {
            return {
                label: 'Removed: ' + change.path,
                note: typeLabelOf(change.node),
                details: affectedDetails(connections, side, change.path),
                change: change
            };
        }

        if (change.kind === 'renamed') {
            return {
                label: 'Renamed: ' + change.path + ' to ' + change.newName,
                note: typeLabelOf(change.node),
                details: affectedDetails(connections, side, change.path),
                change: change
            };
        }

        var out = {
            label: 'Type changed: ' + change.path,
            before: change.from,
            after: change.to,
            details: affectedDetails(connections, side, change.path),
            change: change
        };
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Opens the re-import flow for one side: paste the changed example,
    // review the diff, apply what the review accepts. The example also
    // becomes a new sample, like any other paste.
    // reimportConfig:
    //   store: the artifact store
    //   side:  'source' or 'target'
    zato.mapper.reimport.openDialog = function(reimportConfig) {

        var store = reimportConfig.store;
        var side = reimportConfig.side;

        zato.mapper.dialog.open({
            title: 'Re-import a changed JSON example - ' + side,
            withTextarea: true,
            okLabel: 'Review changes',
            onSubmit: function(result) {

                // Pasted text is an external boundary, parsed explicitly.
                var payload = null;
                try {
                    payload = JSON.parse(result.text);
                } catch(error) {
                    return 'Not valid JSON: ' + error.message;
                }

                var artifact = store.getArtifact();
                var oldRoot = artifact[side + '_schema'].root;
                var newRoot = zato.mapper.schema.inferFromExample(payload);
                var sample = {name: nextSampleName(artifact, side), side: side, payload: payload};

                // With no schema yet there is nothing to diff against -
                // the re-import is a plain first import.
                if (oldRoot === null) {
                    store.applySchemaEdit(side, newRoot, artifact.mappings, artifact.scopes, sample);
                    return;
                }

                var changes = zato.mapper.reimport.diff(oldRoot, newRoot);
                var connections = zato.mapper.connections.list(artifact);

                zato.mapper.log('reimport', 'diff computed', {side: side, changes: changes.length});

                // An identical schema still contributes its sample.
                if (changes.length === 0) {
                    store.addSample(sample);
                }

                var items = [];
                for (var changeIdx = 0; changeIdx < changes.length; changeIdx++) {
                    items.push(reviewItemOf(changes[changeIdx], connections, side));
                }

                zato.mapper.reviewDialog.open({
                    title: 'Re-import review - ' + side,
                    intro: 'Every difference against the current schema, with the mappings it affects. An unaccepted change keeps the current shape. Mappings are never deleted - one referencing a removed field stays and its reference shows up in validation.',
                    emptyText: 'The re-imported example matches the current schema - only the new sample was added.',
                    okLabel: 'Apply selected changes',
                    items: items,
                    onAccept: function(reviewedItems) {

                        var mappings = JSON.parse(JSON.stringify(store.getArtifact().mappings));
                        var scopes = JSON.parse(JSON.stringify(store.getArtifact().scopes));

                        var finalRoot = applyReview(reviewedItems, newRoot, mappings, scopes, side);

                        zato.mapper.log('reimport', 'applying the reviewed changes', {side: side, items: reviewedItems.length});

                        store.applySchemaEdit(side, finalRoot, mappings, scopes, sample);
                    }
                });
            }
        });
    };

})(jQuery);
