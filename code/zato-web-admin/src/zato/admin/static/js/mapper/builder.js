
// Mapper kit - the expression builder.
// A guided editing mode over the same expression string the raw editor
// edits: source fields appear as draggable-free pills, operators and
// functions as chips, and the built expression is always plain text -
// switching to the raw editor and back loses nothing. The builder covers
// the common shape (operands joined by binary operators, optionally
// wrapped in one function call), everything else stays in raw mode.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.builder = {};

// ////////////////////////////////////////////////////////////////////////
// The model - a flat token list plus an optional wrapping function.
// ////////////////////////////////////////////////////////////////////////

    var operandPattern = /^(\d+(?:\.\d+)?|'[^']*'|"[^"]*"|[A-Za-z_][\w.]*)$/;

    function isOperand(token) {

        var out = operandPattern.test(token);
        return out;
    }

    function isOperator(token) {

        var out = config.builderOperators.indexOf(token) !== -1;
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Parses an expression into the builder model when it has the shape
    // the builder covers. Returns {ok, wrap, tokens} - ok false means the
    // expression stays raw-only, with the text preserved untouched.
    zato.mapper.builder.parse = function(text) {

        var out = {ok: false, wrap: '', tokens: []};

        var remaining = text.trim();
        if (remaining === '') {
            out.ok = true;
            return out;
        }

        // An optional single wrapping function call ..
        var wrapMatch = remaining.match(/^(\$[A-Za-z]\w*)\((.*)\)$/);
        if (wrapMatch) {
            out.wrap = wrapMatch[1];
            remaining = wrapMatch[2].trim();
        }

        // .. the rest must be operands joined by binary operators.
        var parts = remaining.match(/('[^']*'|"[^"]*"|[\w.]+|!=|>=|<=|[+\-*\/&=<>])/g);
        if (parts === null) {
            return out;
        }

        // The matched parts must add back up to the whole text - anything
        // unmatched (parentheses, lambdas, filters) keeps the expression raw.
        if (parts.join(' ').replace(/\s+/g, '') !== remaining.replace(/\s+/g, '')) {
            return out;
        }

        for (var partIdx = 0; partIdx < parts.length; partIdx++) {
            var part = parts[partIdx];
            var expectOperand = partIdx % 2 === 0;

            if (expectOperand) {
                if (!isOperand(part)) {
                    return out;
                }
                out.tokens.push({kind: 'operand', value: part});
            }
            else {
                if (!isOperator(part)) {
                    return out;
                }
                out.tokens.push({kind: 'operator', value: part});
            }
        }

        // A trailing operator is not a complete expression.
        var lastToken = out.tokens[out.tokens.length - 1];
        if (lastToken.kind === 'operator') {
            return out;
        }

        out.ok = true;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Serializes the model back into expression text.
    zato.mapper.builder.serialize = function(model) {

        var parts = [];
        for (var tokenIdx = 0; tokenIdx < model.tokens.length; tokenIdx++) {
            parts.push(model.tokens[tokenIdx].value);
        }

        var out = parts.join(' ');
        if (model.wrap !== '') {
            out = model.wrap + '(' + out + ')';
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////
// The UI - a token strip plus controls to add pills, operators,
// literals and a wrapping function.
// ////////////////////////////////////////////////////////////////////////

    // Creates the builder UI inside the container.
    // builderConfig:
    //   container:  the element the builder renders into
    //   paths:      a function returning the source field paths for pills
    //   onChange:   called with the new expression text after every change
    // Returns {setExpression, canBuild}.
    zato.mapper.builder.create = function(builderConfig) {

        var model = {wrap: '', tokens: []};

        var wrapper = document.createElement('div');
        wrapper.className = 'mapper-builder';

        var strip = document.createElement('div');
        strip.className = 'mapper-builder-strip';
        wrapper.appendChild(strip);

        var controls = document.createElement('div');
        controls.className = 'mapper-builder-controls';
        wrapper.appendChild(controls);

        // Field pills come from a dropdown over the source schema paths.
        var fieldSelect = document.createElement('select');
        fieldSelect.className = 'mapper-builder-field-select';
        fieldSelect.setAttribute('aria-label', 'Add a source field');
        controls.appendChild(fieldSelect);

        // Operators are one chip each.
        var operatorRow = document.createElement('span');
        operatorRow.className = 'mapper-builder-operators';
        for (var operatorIdx = 0; operatorIdx < config.builderOperators.length; operatorIdx++) {
            var operatorButton = document.createElement('button');
            operatorButton.className = 'dashboard-pill mapper-builder-operator-chip';
            operatorButton.type = 'button';
            operatorButton.textContent = config.builderOperators[operatorIdx];
            operatorRow.appendChild(operatorButton);
        }
        controls.appendChild(operatorRow);

        // A literal is typed and added explicitly.
        var literalInput = document.createElement('input');
        literalInput.className = 'mapper-builder-literal-input';
        literalInput.type = 'text';
        literalInput.placeholder = 'Literal';
        literalInput.setAttribute('aria-label', 'Add a literal value');
        controls.appendChild(literalInput);

        var literalButton = document.createElement('button');
        literalButton.className = 'mapper-button zato-action-button mapper-builder-literal-add';
        literalButton.type = 'button';
        literalButton.textContent = 'Add literal';
        controls.appendChild(literalButton);

        // The wrapping function comes from the function reference.
        var functionSelect = document.createElement('select');
        functionSelect.className = 'mapper-builder-function-select';
        functionSelect.setAttribute('aria-label', 'Wrap in a function');
        controls.appendChild(functionSelect);

        builderConfig.container.appendChild(wrapper);

// ////////////////////////////////////////////////////////////////////////

        function notify() {
            builderConfig.onChange(zato.mapper.builder.serialize(model));
        }

// ////////////////////////////////////////////////////////////////////////

        function renderStrip() {

            $(strip).empty();

            if (model.wrap !== '') {
                var wrapChip = document.createElement('span');
                wrapChip.className = 'dashboard-pill mapper-builder-chip mapper-builder-chip-function';
                wrapChip.textContent = model.wrap + '(';
                strip.appendChild(wrapChip);
            }

            for (var tokenIdx = 0; tokenIdx < model.tokens.length; tokenIdx++) {
                var token = model.tokens[tokenIdx];

                var chip = document.createElement('span');
                if (token.kind === 'operand') {
                    chip.className = 'dashboard-pill mapper-builder-chip mapper-builder-pill';
                }
                else {
                    chip.className = 'dashboard-pill mapper-builder-chip mapper-builder-chip-operator';
                }
                chip.textContent = token.value;

                var remove = document.createElement('button');
                remove.className = 'mapper-builder-chip-remove';
                remove.type = 'button';
                remove.textContent = '\u00d7';
                remove.setAttribute('data-index', tokenIdx);
                remove.setAttribute('aria-label', 'Remove ' + token.value);
                chip.appendChild(remove);

                strip.appendChild(chip);
            }

            if (model.wrap !== '') {
                var closeChip = document.createElement('span');
                closeChip.className = 'dashboard-pill mapper-builder-chip mapper-builder-chip-function';
                closeChip.textContent = ')';
                strip.appendChild(closeChip);
            }
        }

// ////////////////////////////////////////////////////////////////////////

        function renderControls() {

            // The field dropdown always reflects the current schema ..
            $(fieldSelect).empty();

            var prompt = document.createElement('option');
            prompt.value = '';
            prompt.textContent = 'Add field...';
            fieldSelect.appendChild(prompt);

            var paths = builderConfig.paths();
            for (var pathIdx = 0; pathIdx < paths.length; pathIdx++) {
                var option = document.createElement('option');
                option.value = paths[pathIdx];
                option.textContent = paths[pathIdx];
                fieldSelect.appendChild(option);
            }

            // .. and the function dropdown the function reference,
            // grouped by category.
            $(functionSelect).empty();

            var functionPrompt = document.createElement('option');
            functionPrompt.value = '';
            functionPrompt.textContent = 'Wrap in...';
            functionSelect.appendChild(functionPrompt);

            var unwrap = document.createElement('option');
            unwrap.value = '-';
            unwrap.textContent = 'No function';
            functionSelect.appendChild(unwrap);

            for (var categoryIdx = 0; categoryIdx < config.functionCategories.length; categoryIdx++) {
                var category = config.functionCategories[categoryIdx];

                var group = document.createElement('optgroup');
                group.label = category.label;

                for (var functionIdx = 0; functionIdx < config.functionReference.length; functionIdx++) {
                    var item = config.functionReference[functionIdx];
                    if (item.category !== category.name) {
                        continue;
                    }

                    var functionOption = document.createElement('option');
                    functionOption.value = item.name;
                    functionOption.textContent = item.name + ' - ' + item.doc;
                    group.appendChild(functionOption);
                }

                functionSelect.appendChild(group);
            }
        }

// ////////////////////////////////////////////////////////////////////////

        $(fieldSelect).on('change', function() {
            if (fieldSelect.value === '') {
                return;
            }

            model.tokens.push({kind: 'operand', value: fieldSelect.value});
            fieldSelect.value = '';

            renderStrip();
            notify();
        });

        $(operatorRow).on('click', '.mapper-builder-operator-chip', function() {
            model.tokens.push({kind: 'operator', value: $(this).text()});
            renderStrip();
            notify();
        });

        $(literalButton).on('click', function() {
            if (literalInput.value === '') {
                return;
            }

            // A value that is not a number becomes a quoted string.
            var value = literalInput.value;
            if (!/^\d+(\.\d+)?$/.test(value)) {
                value = "'" + value.replace(/'/g, '') + "'";
            }

            model.tokens.push({kind: 'operand', value: value});
            literalInput.value = '';

            renderStrip();
            notify();
        });

        $(functionSelect).on('change', function() {
            if (functionSelect.value === '') {
                return;
            }

            model.wrap = functionSelect.value === '-' ? '' : functionSelect.value;
            functionSelect.value = '';

            renderStrip();
            notify();
        });

        $(strip).on('click', '.mapper-builder-chip-remove', function() {
            model.tokens.splice(parseInt($(this).attr('data-index'), 10), 1);
            renderStrip();
            notify();
        });

        renderControls();
        renderStrip();

        return {

            // Loads an expression into the builder. Returns whether the
            // expression has the shape the builder covers.
            setExpression: function(text) {

                var parsed = zato.mapper.builder.parse(text);
                if (parsed.ok) {
                    model.wrap = parsed.wrap;
                    model.tokens = parsed.tokens;
                    renderControls();
                    renderStrip();
                }

                return parsed.ok;
            },

            canBuild: function(text) {

                var out = zato.mapper.builder.parse(text).ok;
                return out;
            }
        };
    };

})(jQuery);
