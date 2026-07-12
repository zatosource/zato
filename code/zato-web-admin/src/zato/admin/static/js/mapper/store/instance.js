
// Mapper kit - the store instance.
// Holds one artifact, applies validated mutations, keeps undo and redo
// snapshots and autosaves to browser storage after every change.
// Everything the UI shows is a projection of this store and every
// change goes through one of its mutations.

(function($) {

    var config = zato.mapper.config;

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.store.create = function(createConfig) {

        var artifact;
        var undoStack = [];
        var redoStack = [];
        var listeners = [];
        var storageKey = createConfig.storageKey;

        // Restore the autosaved artifact if browser storage has a valid one,
        // otherwise start from an empty artifact. Storage content is an
        // external boundary, so it is parsed and validated explicitly.
        var saved = window.store.get(storageKey);
        if (saved) {
            var parsed = null;
            try {
                parsed = JSON.parse(saved);
            } catch(error) {
                parsed = null;
                zato.mapper.log('store', 'the autosaved artifact is not valid JSON', {storageKey: storageKey, error: error.message});
            }
            if (parsed) {
                var savedRecords = zato.mapper.store.validate(parsed);
                if (savedRecords.length === 0) {
                    artifact = parsed;
                }
                else {
                    zato.mapper.log('store', 'the autosaved artifact failed validation and is discarded', {storageKey: storageKey, records: savedRecords});
                }
            }
        }
        if (artifact) {
            zato.mapper.log('store', 'restored the autosaved artifact', {storageKey: storageKey, name: artifact.name, mappings: artifact.mappings.length, scopes: artifact.scopes.length, samples: artifact.samples.length});
        }
        else {
            artifact = zato.mapper.store.newArtifact();
            zato.mapper.log('store', 'started with a new, empty artifact', {storageKey: storageKey});
        }

        function notify() {
            for (var listenerIdx = 0; listenerIdx < listeners.length; listenerIdx++) {
                listeners[listenerIdx](artifact);
            }
        }

        function snapshot() {
            var out = zato.mapper.store.serialize(artifact);
            return out;
        }

        function autosave() {
            window.store.set(storageKey, snapshot());
        }

        // Every mutation runs through here: the previous state goes onto
        // the undo stack, the redo stack is cleared, the change is applied,
        // then the artifact is autosaved, logged and all listeners re-render.
        function mutate(label, data, applyChange) {
            undoStack.push(snapshot());
            if (undoStack.length > config.undoLimit) {
                undoStack.shift();
            }
            redoStack = [];

            applyChange(artifact);

            autosave();

            zato.mapper.log('store', 'mutation ' + label, data);

            var records = zato.mapper.store.validate(artifact);
            if (records.length > 0) {
                zato.mapper.log('store', 'the artifact has validation records after ' + label, records);
            }

            notify();
        }

        var instance = {

            getArtifact: function() {
                return artifact;
            },

            serialize: function() {
                var out = snapshot();
                return out;
            },

            validate: function() {
                var out = zato.mapper.store.validate(artifact);
                return out;
            },

            subscribe: function(listener) {
                listeners.push(listener);
            },

            // Replaces the whole artifact, e.g. from an imported file.
            // Returns the validation records - the artifact is replaced
            // only when the list is empty.
            loadArtifact: function(candidate) {
                var records = zato.mapper.store.validate(candidate);
                if (records.length === 0) {
                    mutate('loadArtifact', {name: candidate.name}, function() {
                        artifact = candidate;
                    });
                }
                else {
                    zato.mapper.log('store', 'loadArtifact rejected the candidate', records);
                }

                return records;
            },

            setName: function(name) {
                mutate('setName', {name: name}, function(current) {
                    current.name = name;
                });
            },

            setDescription: function(description) {
                mutate('setDescription', {description: description}, function(current) {
                    current.description = description;
                });
            },

            // Replaces one side's schema tree. The side is 'source' or 'target'.
            setSchemaRoot: function(side, root) {
                mutate('setSchemaRoot', {side: side}, function(current) {
                    current[side + '_schema'].root = root;
                });
            },

            addSample: function(sample) {
                mutate('addSample', {name: sample.name, side: sample.side}, function(current) {
                    current.samples.push(sample);
                });
            },

            addMapping: function(row) {
                mutate('addMapping', row, function(current) {
                    current.mappings.push(row);
                });
            },

            updateMapping: function(rowIndex, row) {
                mutate('updateMapping', {rowIndex: rowIndex, row: row}, function(current) {
                    current.mappings[rowIndex] = row;
                });
            },

            removeMapping: function(rowIndex) {
                mutate('removeMapping', {rowIndex: rowIndex}, function(current) {
                    current.mappings.splice(rowIndex, 1);
                });
            },

            addScope: function(scope) {
                mutate('addScope', {target: scope.target, source: scope.source, rows: scope.mappings.length}, function(current) {
                    current.scopes.push(scope);
                });
            },

            addScopeMapping: function(scopeIndex, row) {
                mutate('addScopeMapping', {scopeIndex: scopeIndex, row: row}, function(current) {
                    current.scopes[scopeIndex].mappings.push(row);
                });
            },

            updateScopeMapping: function(scopeIndex, rowIndex, row) {
                mutate('updateScopeMapping', {scopeIndex: scopeIndex, rowIndex: rowIndex, row: row}, function(current) {
                    current.scopes[scopeIndex].mappings[rowIndex] = row;
                });
            },

            removeScopeMapping: function(scopeIndex, rowIndex) {
                mutate('removeScopeMapping', {scopeIndex: scopeIndex, rowIndex: rowIndex}, function(current) {
                    current.scopes[scopeIndex].mappings.splice(rowIndex, 1);
                });
            },

            // Applies accepted auto-map suggestions in one undoable step:
            // new top-level rows, new scopes with their children, and
            // child rows added into scopes that already exist.
            applyAutoMap: function(rows, scopes, scopeAdditions) {
                mutate('applyAutoMap', {rows: rows.length, scopes: scopes.length, additions: scopeAdditions.length}, function(current) {

                    for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
                        current.mappings.push(rows[rowIdx]);
                    }

                    for (var scopeIdx = 0; scopeIdx < scopes.length; scopeIdx++) {
                        current.scopes.push(scopes[scopeIdx]);
                    }

                    for (var additionIdx = 0; additionIdx < scopeAdditions.length; additionIdx++) {
                        var addition = scopeAdditions[additionIdx];
                        for (var childIdx = 0; childIdx < addition.rows.length; childIdx++) {
                            current.scopes[addition.scopeIndex].mappings.push(addition.rows[childIdx]);
                        }
                    }
                });
            },

            // Replaces one side's schema tree together with the whole
            // mapping and scope lists in one undoable step - the shape
            // a field rename or a schema re-import produces. The sample
            // is null when the edit brings no new sample along.
            applySchemaEdit: function(side, root, mappings, scopes, sample) {
                mutate('applySchemaEdit', {side: side, mappings: mappings.length, scopes: scopes.length}, function(current) {
                    current[side + '_schema'].root = root;
                    current.mappings = mappings;
                    current.scopes = scopes;

                    if (sample !== null) {
                        current.samples.push(sample);
                    }
                });
            },

            // Removes every mapping row and scope in one undoable step.
            clearMappings: function() {
                mutate('clearMappings', {}, function(current) {
                    current.mappings = [];
                    current.scopes = [];
                });
            },

            canUndo: function() {
                var out = undoStack.length > 0;
                return out;
            },

            canRedo: function() {
                var out = redoStack.length > 0;
                return out;
            },

            undo: function() {
                if (undoStack.length === 0) {
                    return;
                }

                // The current state becomes redoable, the previous one current.
                redoStack.push(snapshot());
                artifact = JSON.parse(undoStack.pop());

                autosave();
                zato.mapper.log('store', 'undo', {undoLeft: undoStack.length, redoLeft: redoStack.length});
                notify();
            },

            redo: function() {
                if (redoStack.length === 0) {
                    return;
                }

                // The current state becomes undoable again, the redone one current.
                undoStack.push(snapshot());
                artifact = JSON.parse(redoStack.pop());

                autosave();
                zato.mapper.log('store', 'redo', {undoLeft: undoStack.length, redoLeft: redoStack.length});
                notify();
            }
        };

        return instance;
    };

})(jQuery);
