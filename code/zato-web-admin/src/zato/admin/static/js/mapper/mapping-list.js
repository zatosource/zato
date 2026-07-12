
// Mapper kit - the mapping list.
// The flat list of every mapping row - each row reads from source to
// target: the expression first, then the target it writes, then the
// value it evaluated to against the active sample and its own error
// when it has one. Scopes render as groups with their
// child rows and a per-element picker for previewing one element at
// a time. A mapping too complex to draw anywhere else is still always
// visible here.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.mappingList = {};

// ////////////////////////////////////////////////////////////////////////

    // Initializes the list.
    // listConfig:
    //   store:      the artifact store
    //   container:  the element the list renders into
    //   addButton:  the button creating a new row
    //   onSelect:   called with {scopeIndex, rowIndex} or null on deselect
    // Returns {setResults, select, deselect, getSelected, getElementIndex}.
    zato.mapper.mappingList.init = function(listConfig) {

        var store = listConfig.store;
        var container = listConfig.container;

        var selected = null;
        var results = null;
        var elementIndexes = {};

// ////////////////////////////////////////////////////////////////////////

        function formatValue(value) {

            if (value === undefined) {
                return config.previewEmptyValueLabel;
            }

            var out = JSON.stringify(value);
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // The results may lag one change behind the artifact - a row or
        // a scope added a moment ago has no result yet, which reads the
        // same as having no results at all.
        function rowResultOf(scopeIndex, rowIndex) {

            if (results === null) {
                return null;
            }

            if (scopeIndex === null) {
                var out = results.rows[rowIndex];
                if (out === undefined) {
                    return null;
                }
                return out;
            }

            var scopeResult = results.scopes[scopeIndex];
            if (scopeResult === undefined) {
                return null;
            }
            if (scopeResult.elements.length === 0) {
                return null;
            }

            var elementIdx = elementIndexes[scopeIndex];
            if (elementIdx === undefined) {
                elementIdx = 0;
            }

            var elementResults = scopeResult.elements[elementIdx];
            var childOut = elementResults[rowIndex];
            if (childOut === undefined) {
                return null;
            }
            return childOut;
        }

// ////////////////////////////////////////////////////////////////////////

        function buildRow(row, scopeIndex, rowIndex) {

            var item = document.createElement('li');
            item.className = 'mapper-row';
            if (selected !== null) {
                if (selected.scopeIndex === scopeIndex) {
                    if (selected.rowIndex === rowIndex) {
                        item.className = 'mapper-row mapper-row-selected';
                    }
                }
            }
            item.setAttribute('tabindex', '0');
            item.setAttribute('data-scope-index', scopeIndex === null ? '' : scopeIndex);
            item.setAttribute('data-row-index', rowIndex);

            var expression = document.createElement('span');
            expression.className = 'mapper-row-expression';
            expression.textContent = row.expression;
            item.appendChild(expression);

            var arrow = document.createElement('span');
            arrow.className = 'mapper-row-arrow';
            arrow.textContent = '\u2192';
            item.appendChild(arrow);

            var target = document.createElement('span');
            target.className = 'mapper-row-target';
            target.textContent = row.target === '' ? '(no target)' : row.target;
            item.appendChild(target);

            // The inline evaluated value or the row's own error.
            var result = rowResultOf(scopeIndex, rowIndex);
            if (result !== null) {
                if (result.error !== '') {
                    var error = document.createElement('span');
                    error.className = 'dashboard-outcome-badge mapper-row-error';
                    error.textContent = result.error;
                    item.appendChild(error);
                }
                else if (result.skipped) {
                    var skipped = document.createElement('span');
                    skipped.className = 'dashboard-outcome-badge mapper-row-note';
                    skipped.textContent = 'skipped';
                    item.appendChild(skipped);
                }
                else if (result.omitted) {
                    var omitted = document.createElement('span');
                    omitted.className = 'dashboard-outcome-badge mapper-row-note';
                    omitted.textContent = 'omitted';
                    item.appendChild(omitted);
                }
                else {
                    var value = document.createElement('span');
                    value.className = 'dashboard-outcome-badge mapper-row-value';
                    value.textContent = formatValue(result.value);
                    item.appendChild(value);
                }
            }

            // Top-level rows can be removed from the list directly.
            if (scopeIndex === null) {
                var remove = document.createElement('button');
                remove.className = 'mapper-row-remove';
                remove.type = 'button';
                remove.textContent = '\u00d7';
                remove.setAttribute('aria-label', 'Remove mapping');
                remove.setAttribute('data-remove-index', rowIndex);
                item.appendChild(remove);
            }

            return item;
        }

// ////////////////////////////////////////////////////////////////////////

        function buildScopeGroup(scope, scopeIndex) {

            var group = document.createElement('li');
            group.className = 'mapper-scope-group';

            var header = document.createElement('div');
            header.className = 'mapper-scope-header';

            var title = document.createElement('span');
            title.className = 'mapper-scope-title';
            title.textContent = 'each ' + scope.source + ' \u2192 ' + scope.target;
            header.appendChild(title);

            // The element picker shows one element's child values at a time.
            // A scope added a moment ago has no result until the next run.
            if (results !== null && results.scopes[scopeIndex] !== undefined) {
                var scopeResult = results.scopes[scopeIndex];
                if (scopeResult.length > 0) {
                    var picker = document.createElement('select');
                    picker.className = 'mapper-scope-element-picker';
                    picker.setAttribute('aria-label', 'Preview element');
                    picker.setAttribute('data-scope-index', scopeIndex);

                    for (var elementIdx = 0; elementIdx < scopeResult.length; elementIdx++) {
                        var option = document.createElement('option');
                        option.value = elementIdx;
                        option.textContent = 'Element ' + (elementIdx + 1) + ' of ' + scopeResult.length;
                        picker.appendChild(option);
                    }

                    var currentIdx = elementIndexes[scopeIndex];
                    if (currentIdx !== undefined) {
                        picker.value = currentIdx;
                    }

                    header.appendChild(picker);
                }

                if (scopeResult.error !== '') {
                    var error = document.createElement('span');
                    error.className = 'dashboard-outcome-badge mapper-row-error';
                    error.textContent = scopeResult.error;
                    header.appendChild(error);
                }
            }

            group.appendChild(header);

            var childList = document.createElement('ul');
            childList.className = 'mapper-scope-rows';

            for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                childList.appendChild(buildRow(scope.mappings[childIdx], scopeIndex, childIdx));
            }

            group.appendChild(childList);

            return group;
        }

// ////////////////////////////////////////////////////////////////////////

        function render() {

            var artifact = store.getArtifact();

            $(container).empty();

            var hasRows = artifact.mappings.length > 0;
            var hasScopes = artifact.scopes.length > 0;

            if (!hasRows) {
                if (!hasScopes) {
                    var empty = document.createElement('div');
                    empty.className = 'mapper-empty-state';

                    var title = document.createElement('h3');
                    title.className = 'mapper-empty-state-title';
                    title.textContent = 'No mappings yet';
                    empty.appendChild(title);

                    var text = document.createElement('p');
                    text.className = 'mapper-empty-state-text';
                    text.textContent = 'Drag a source field onto a target field above, or add a mapping by hand.';
                    empty.appendChild(text);

                    container.appendChild(empty);
                    return;
                }
            }

            var list = document.createElement('ul');
            list.className = 'mapper-rows';

            for (var rowIdx = 0; rowIdx < artifact.mappings.length; rowIdx++) {
                list.appendChild(buildRow(artifact.mappings[rowIdx], null, rowIdx));
            }

            for (var scopeIdx = 0; scopeIdx < artifact.scopes.length; scopeIdx++) {
                list.appendChild(buildScopeGroup(artifact.scopes[scopeIdx], scopeIdx));
            }

            container.appendChild(list);
        }

// ////////////////////////////////////////////////////////////////////////

        function select(scopeIndex, rowIndex) {
            selected = {scopeIndex: scopeIndex, rowIndex: rowIndex};
            zato.mapper.log('mapping-list', 'row selected', selected);
            render();
            listConfig.onSelect(selected);
        }

// ////////////////////////////////////////////////////////////////////////

        $(container).on('click', '.mapper-row', function(event) {

            // The remove button inside the row acts on its own.
            if ($(event.target).hasClass('mapper-row-remove')) {
                return;
            }

            var scopeAttribute = $(this).attr('data-scope-index');
            var scopeIndex = scopeAttribute === '' ? null : parseInt(scopeAttribute, 10);
            var rowIndex = parseInt($(this).attr('data-row-index'), 10);

            select(scopeIndex, rowIndex);
        });

        $(container).on('click', '.mapper-row-remove', function() {

            var rowIndex = parseInt($(this).attr('data-remove-index'), 10);

            selected = null;
            listConfig.onSelect(null);
            store.removeMapping(rowIndex);
        });

        $(container).on('change', '.mapper-scope-element-picker', function() {
            var scopeIndex = parseInt($(this).attr('data-scope-index'), 10);
            elementIndexes[scopeIndex] = parseInt(this.value, 10);
            render();
        });

        $(listConfig.addButton).on('click', function() {

            var row = zato.mapper.store.newMapping();
            store.addMapping(row);

            // The new row is selected right away for editing.
            select(null, store.getArtifact().mappings.length - 1);
        });

        store.subscribe(function() {

            // A mutation may have removed the selected row.
            var artifact = store.getArtifact();
            if (selected !== null) {
                if (selected.scopeIndex === null) {
                    if (selected.rowIndex >= artifact.mappings.length) {
                        selected = null;
                        listConfig.onSelect(null);
                    }
                }
            }

            render();
        });

        render();

        return {

            setResults: function(newResults) {
                results = newResults;
                render();
            },

            select: function(selection) {
                select(selection.scopeIndex, selection.rowIndex);
            },

            deselect: function() {

                if (selected === null) {
                    return;
                }

                selected = null;
                zato.mapper.log('mapping-list', 'row deselected', {});
                render();
                listConfig.onSelect(null);
            },

            getSelected: function() {
                return selected;
            },

            getElementIndex: function(scopeIndex) {

                var out = elementIndexes[scopeIndex];
                if (out === undefined) {
                    out = 0;
                }

                return out;
            }
        };
    };

})(jQuery);
