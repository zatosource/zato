
// Mapper kit - the live preview.
// An editable input pane holding the active source sample and an
// output pane showing the mapping's result against it, re-evaluated
// on every change - including pending, not-yet-committed edits from
// the detail panel and edits typed straight into the input pane.
// Both panes are collapsible and stay visible otherwise.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.preview = {};

// ////////////////////////////////////////////////////////////////////////

    // Initializes the preview.
    // previewConfig:
    //   store:      the artifact store
    //   onResults:  called with the evaluator results after every run
    // Returns {setPending, clearPending, getActiveSample}.
    zato.mapper.preview.init = function(previewConfig) {

        var store = previewConfig.store;

        var sampleSelect = document.getElementById('mapper-preview-sample-select');
        var inputPane = document.getElementById('mapper-preview-input');
        var outputPane = document.getElementById('mapper-preview-output');
        var inputToggle = document.getElementById('mapper-preview-input-toggle');
        var outputToggle = document.getElementById('mapper-preview-output-toggle');

        var pending = null;
        var runCounter = 0;

        // A payload typed into the input pane - it overrides the active
        // sample until another sample is picked, without being stored.
        var editedPayload = null;

// ////////////////////////////////////////////////////////////////////////

        function sourceSamples() {

            var samples = store.getArtifact().samples;

            var out = [];
            for (var sampleIdx = 0; sampleIdx < samples.length; sampleIdx++) {
                if (samples[sampleIdx].side === 'source') {
                    out.push(samples[sampleIdx]);
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function activeSample() {

            var samples = sourceSamples();
            if (samples.length === 0) {
                return null;
            }

            // The remembered choice wins as long as it still exists.
            var remembered = window.store.get(config.activeSampleStorageKey);
            for (var sampleIdx = 0; sampleIdx < samples.length; sampleIdx++) {
                if (samples[sampleIdx].name === remembered) {
                    return samples[sampleIdx];
                }
            }

            var out = samples[0];
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function renderSampleSelect() {

            var samples = sourceSamples();
            var active = activeSample();

            $(sampleSelect).empty();

            for (var sampleIdx = 0; sampleIdx < samples.length; sampleIdx++) {
                var option = document.createElement('option');
                option.value = samples[sampleIdx].name;
                option.textContent = samples[sampleIdx].name;
                sampleSelect.appendChild(option);
            }

            if (active !== null) {
                sampleSelect.value = active.name;
            }
        }

// ////////////////////////////////////////////////////////////////////////

        // The artifact with any pending row edit substituted in - the
        // preview always follows what the user sees, committed or not.
        function effectiveArtifact() {

            var artifact = JSON.parse(store.serialize());

            if (pending !== null) {
                if (pending.selection.scopeIndex === null) {
                    artifact.mappings[pending.selection.rowIndex] = pending.row;
                }
                else {
                    artifact.scopes[pending.selection.scopeIndex].mappings[pending.selection.rowIndex] = pending.row;
                }
            }

            return artifact;
        }

// ////////////////////////////////////////////////////////////////////////

        async function run() {

            runCounter += 1;
            var thisRun = runCounter;

            renderSampleSelect();

            var sample = activeSample();
            if (sample === null) {
                zato.mapper.log('preview', 'no source sample, nothing to evaluate');
                inputPane.innerHTML = '<span class="mapper-preview-empty">No source sample yet - paste an example or scaffold one from the schema.</span>';
                outputPane.innerHTML = '<span class="mapper-preview-empty">The output appears here once a sample exists.</span>';
                return;
            }

            zato.mapper.log('preview', 'evaluating against the active sample', {sample: sample.name, pending: pending !== null, edited: editedPayload !== null});

            // The edited input wins over the stored sample.
            var payload = editedPayload === null ? sample.payload : editedPayload;

            // Re-rendering the input while the user types in it would
            // destroy their caret, so the pane only re-renders when its
            // text is not the user's own.
            if (editedPayload === null && document.activeElement !== inputPane) {
                var inputText = JSON.stringify(payload, null, config.jsonIndent);
                inputPane.innerHTML = zato.mapper.highlight.json(inputText);
            }

            var results = await zato.mapper.evaluator.run(effectiveArtifact(), payload);

            // A newer run may have started while this one was evaluating.
            if (thisRun !== runCounter) {
                return;
            }

            var outputText = JSON.stringify(results.output, null, config.jsonIndent);
            outputPane.innerHTML = zato.mapper.highlight.json(outputText);

            previewConfig.onResults(results);
        }

// ////////////////////////////////////////////////////////////////////////

        $(sampleSelect).on('change', function() {
            zato.mapper.log('preview', 'active sample changed', {sample: sampleSelect.value});
            window.store.set(config.activeSampleStorageKey, sampleSelect.value);

            // Picking a sample discards any edits typed into the input.
            editedPayload = null;
            inputPane.classList.remove('mapper-preview-input-invalid');

            var _ = run();
        });

        // Typing into the input pane re-evaluates the output live -
        // text that stops being valid JSON marks the pane and keeps
        // the last good output on show.
        $(inputPane).on('input', function() {

            var parsed;
            try {
                parsed = JSON.parse(inputPane.textContent);
            }
            catch (parseError) {
                zato.mapper.log('preview', 'the edited input is not valid JSON', {error: parseError.message});
                inputPane.classList.add('mapper-preview-input-invalid');
                return;
            }

            inputPane.classList.remove('mapper-preview-input-invalid');
            editedPayload = parsed;

            var _ = run();
        });

        // Leaving the pane re-applies the syntax colors the plain-text
        // editing stripped away - only when the text parses, an invalid
        // draft stays as typed.
        $(inputPane).on('blur', function() {

            if (editedPayload === null) {
                return;
            }

            if (inputPane.classList.contains('mapper-preview-input-invalid')) {
                return;
            }

            var editedText = JSON.stringify(editedPayload, null, config.jsonIndent);
            inputPane.innerHTML = zato.mapper.highlight.json(editedText);
        });

        $(inputToggle).on('click', function() {
            inputPane.hidden = !inputPane.hidden;
        });

        $(outputToggle).on('click', function() {
            outputPane.hidden = !outputPane.hidden;
        });

        store.subscribe(function() {

            // A committed edit replaces any pending state.
            pending = null;
            var _ = run();
        });

        var _ = run();

        return {

            setPending: function(selection, row) {
                pending = {selection: selection, row: row};
                var pendingRun = run();
                _ = pendingRun;
            },

            clearPending: function() {
                pending = null;
                var clearedRun = run();
                _ = clearedRun;
            },

            getActiveSample: activeSample
        };
    };

})(jQuery);
