
// Mapper kit - named schemas.
// Stored once in browser storage, referenced by many mappings.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.schema.named = {};

// ////////////////////////////////////////////////////////////////////////

    function readNamed() {

        // Browser storage is an external boundary, so absence is explicit.
        var saved = window.store.get(config.namedSchemasStorageKey);
        if (!saved) {
            return {};
        }

        var out = JSON.parse(saved);
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.schema.named.list = function() {

        var byName = readNamed();

        var out = [];
        for (var name in byName) {
            out.push(name);
        }
        out.sort();

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.schema.named.get = function(name) {
        var byName = readNamed();

        var out = byName[name];
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.schema.named.save = function(name, root) {
        var byName = readNamed();
        byName[name] = root;
        window.store.set(config.namedSchemasStorageKey, JSON.stringify(byName));
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.schema.named.remove = function(name) {
        var byName = readNamed();
        delete byName[name];
        window.store.set(config.namedSchemasStorageKey, JSON.stringify(byName));
    };

})(jQuery);
