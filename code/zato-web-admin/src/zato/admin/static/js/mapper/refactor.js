
// Mapper kit - field renames.
// Renaming a schema field propagates into everything that references
// it: expressions, conditions, iteration scope selectors and target
// paths, each shown in a review list first with per-item accept. An
// update left unaccepted keeps its old text and the validation of the
// unresolvable reference stays loud - nothing breaks silently.

(function($) {

    zato.mapper.refactor = {};

// ////////////////////////////////////////////////////////////////////////

    // What a field may be renamed to - one identifier, no dots.
    var fieldNamePattern = /^[A-Za-z_][A-Za-z0-9_]*$/;

// ////////////////////////////////////////////////////////////////////////

    // Rewrites the dotted-path references inside one expression text.
    // Quoted strings and $function names pass through untouched, and a
    // reference only rewrites on a whole-token match, so `customer` in
    // `customer_group` never changes.
    zato.mapper.refactor.rewriteExpression = function(expression, oldPath, newPath) {

        var tokenPattern = /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`[^`]*`|\$?[A-Za-z_][\w.]*/g;

        var out = expression.replace(tokenPattern, function(token) {

            // String literals, backtick names and $functions stay as they are.
            var firstCharacter = token.charAt(0);
            if (firstCharacter === '"' || firstCharacter === "'" || firstCharacter === '`' || firstCharacter === '$') {
                return token;
            }

            if (token === oldPath) {
                return newPath;
            }
            if (token.indexOf(oldPath + '.') === 0) {
                return newPath + token.substring(oldPath.length);
            }

            return token;
        });

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Rewrites one dotted path when it equals the renamed path or
    // lives inside its subtree.
    function rewritePath(path, oldPath, newPath) {

        if (path === oldPath) {
            return newPath;
        }
        if (path.indexOf(oldPath + '.') === 0) {
            return newPath + path.substring(oldPath.length);
        }

        return path;
    }

    zato.mapper.refactor.rewritePath = rewritePath;

// ////////////////////////////////////////////////////////////////////////

    // One rewrite descriptor and review item in a single object:
    // where the new text goes (area, scopeIndex, rowIndex, field)
    // plus what the review list shows (label, note, before, after).
    function newRewrite(area, scopeIndex, rowIndex, field, label, note, before, after) {
        return {
            area: area,
            scopeIndex: scopeIndex,
            rowIndex: rowIndex,
            field: field,
            label: label,
            note: note,
            before: before,
            after: after
        };
    }

// ////////////////////////////////////////////////////////////////////////

    // Collects every rewrite renaming a source-side field causes:
    // expressions and conditions of top-level rows, scope selectors,
    // and - relative to their scope - child row expressions.
    function sourceRewrites(mappings, scopes, oldPath, newPath) {

        var out = [];

        for (var rowIdx = 0; rowIdx < mappings.length; rowIdx++) {
            var row = mappings[rowIdx];

            var newExpression = zato.mapper.refactor.rewriteExpression(row.expression, oldPath, newPath);
            if (newExpression !== row.expression) {
                out.push(newRewrite('mapping', null, rowIdx, 'expression', row.target, 'expression', row.expression, newExpression));
            }

            var newCondition = zato.mapper.refactor.rewriteExpression(row.condition, oldPath, newPath);
            if (newCondition !== row.condition) {
                out.push(newRewrite('mapping', null, rowIdx, 'condition', row.target, 'condition', row.condition, newCondition));
            }
        }

        for (var scopeIdx = 0; scopeIdx < scopes.length; scopeIdx++) {
            var scope = scopes[scopeIdx];

            var newSource = zato.mapper.refactor.rewriteExpression(scope.source, oldPath, newPath);
            if (newSource !== scope.source) {
                out.push(newRewrite('scope', scopeIdx, null, 'source', scope.target, 'iteration source', scope.source, newSource));
            }

            // Child expressions are relative to the scope selector, so the
            // renamed path only reaches them when it lies inside that subtree.
            if (oldPath.indexOf(scope.source + '.') !== 0) {
                continue;
            }

            var relativeOld = oldPath.substring(scope.source.length + 1);
            var relativeNew = newPath.substring(scope.source.length + 1);

            for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                var childRow = scope.mappings[childIdx];
                var childLabel = scope.target + '.' + childRow.target;

                var newChildExpression = zato.mapper.refactor.rewriteExpression(childRow.expression, relativeOld, relativeNew);
                if (newChildExpression !== childRow.expression) {
                    out.push(newRewrite('scope-mapping', scopeIdx, childIdx, 'expression', childLabel, 'expression', childRow.expression, newChildExpression));
                }

                var newChildCondition = zato.mapper.refactor.rewriteExpression(childRow.condition, relativeOld, relativeNew);
                if (newChildCondition !== childRow.condition) {
                    out.push(newRewrite('scope-mapping', scopeIdx, childIdx, 'condition', childRow.condition, 'condition', childRow.condition, newChildCondition));
                }
            }
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Collects every rewrite renaming a target-side field causes:
    // target paths of rows and scopes, absolute or scope-relative.
    function targetRewrites(mappings, scopes, oldPath, newPath) {

        var out = [];

        for (var rowIdx = 0; rowIdx < mappings.length; rowIdx++) {
            var row = mappings[rowIdx];

            var newTarget = rewritePath(row.target, oldPath, newPath);
            if (newTarget !== row.target) {
                out.push(newRewrite('mapping', null, rowIdx, 'target', row.target, 'target path', row.target, newTarget));
            }
        }

        for (var scopeIdx = 0; scopeIdx < scopes.length; scopeIdx++) {
            var scope = scopes[scopeIdx];

            var newScopeTarget = rewritePath(scope.target, oldPath, newPath);
            if (newScopeTarget !== scope.target) {
                out.push(newRewrite('scope', scopeIdx, null, 'target', scope.target, 'iteration target', scope.target, newScopeTarget));
            }

            // Child targets are relative to the scope target, so the
            // renamed path only reaches them from inside that subtree.
            if (oldPath.indexOf(scope.target + '.') !== 0) {
                continue;
            }

            var relativeOld = oldPath.substring(scope.target.length + 1);
            var relativeNew = newPath.substring(scope.target.length + 1);

            for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                var childRow = scope.mappings[childIdx];

                var newChildTarget = rewritePath(childRow.target, relativeOld, relativeNew);
                if (newChildTarget !== childRow.target) {
                    var childLabel = scope.target + '.' + childRow.target;
                    out.push(newRewrite('scope-mapping', scopeIdx, childIdx, 'target', childLabel, 'target path', childRow.target, newChildTarget));
                }
            }
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Returns every rewrite renaming the field at oldPath to newPath
    // causes across the given rows and scopes.
    zato.mapper.refactor.renameRewrites = function(mappings, scopes, side, oldPath, newPath) {

        var out;
        if (side === 'source') {
            out = sourceRewrites(mappings, scopes, oldPath, newPath);
        }
        else {
            out = targetRewrites(mappings, scopes, oldPath, newPath);
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Writes accepted rewrites into the row and scope lists in place.
    zato.mapper.refactor.applyRewrites = function(mappings, scopes, rewrites) {

        for (var rewriteIdx = 0; rewriteIdx < rewrites.length; rewriteIdx++) {
            var rewrite = rewrites[rewriteIdx];

            if (rewrite.area === 'mapping') {
                mappings[rewrite.rowIndex][rewrite.field] = rewrite.after;
            }
            else if (rewrite.area === 'scope') {
                scopes[rewrite.scopeIndex][rewrite.field] = rewrite.after;
            }
            else {
                scopes[rewrite.scopeIndex].mappings[rewrite.rowIndex][rewrite.field] = rewrite.after;
            }
        }
    };

// ////////////////////////////////////////////////////////////////////////

    // Opens the rename dialog for one field, then - when anything
    // references it - the review list of every propagated update.
    // renameConfig:
    //   store: the artifact store
    //   side:  'source' or 'target'
    //   path:  the dotted path of the renamed field
    zato.mapper.refactor.openRenameDialog = function(renameConfig) {

        var store = renameConfig.store;
        var side = renameConfig.side;
        var path = renameConfig.path;

        zato.mapper.dialog.open({
            title: 'Rename ' + side + ' field ' + path,
            withInput: true,
            inputLabel: 'New name',
            okLabel: 'Rename',
            onSubmit: function(result) {

                var newName = result.value.trim();
                if (!fieldNamePattern.test(newName)) {
                    return 'A field name is one word of letters, digits and underscores, starting with a letter or an underscore';
                }

                // The rename applies to a copy of the tree first ..
                var artifact = store.getArtifact();
                var renamed = zato.mapper.schema.renameField(artifact[side + '_schema'].root, path, newName);
                if (renamed.error !== '') {
                    return renamed.error;
                }

                // .. the new path shares the parent, only the last segment changes ..
                var segments = path.split('.');
                segments[segments.length - 1] = newName;
                var newPath = segments.join('.');

                // .. everything referencing the field is found on copies
                // of the rows and scopes ..
                var mappings = JSON.parse(JSON.stringify(artifact.mappings));
                var scopes = JSON.parse(JSON.stringify(artifact.scopes));
                var rewrites = zato.mapper.refactor.renameRewrites(mappings, scopes, side, path, newPath);

                zato.mapper.log('refactor', 'rename planned', {side: side, path: path, newPath: newPath, rewrites: rewrites.length});

                // .. with nothing referencing it, the rename is the whole change ..
                if (rewrites.length === 0) {
                    store.applySchemaEdit(side, renamed.root, mappings, scopes, null);
                    return;
                }

                // .. otherwise every propagated update goes through review.
                zato.mapper.reviewDialog.open({
                    title: 'Rename ' + path + ' to ' + newName,
                    intro: 'The rename updates everything that references the field - review each update, an unaccepted one keeps its old text.',
                    emptyText: '',
                    okLabel: 'Rename and update',
                    items: rewrites,
                    onAccept: function(items) {

                        var accepted = [];
                        for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
                            if (items[itemIdx].checked) {
                                accepted.push(items[itemIdx]);
                            }
                        }

                        zato.mapper.log('refactor', 'rename applied', {side: side, path: path, newPath: newPath, accepted: accepted.length, total: items.length});

                        zato.mapper.refactor.applyRewrites(mappings, scopes, accepted);
                        store.applySchemaEdit(side, renamed.root, mappings, scopes, null);
                    }
                });
            }
        });
    };

})(jQuery);
