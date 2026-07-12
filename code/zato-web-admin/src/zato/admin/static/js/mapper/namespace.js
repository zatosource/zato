
// Mapper kit - root namespace and configuration defaults.
// Every other kit file attaches to zato.mapper and reads its defaults
// from zato.mapper.config, so this file always loads first.

(function($) {

    // The page may be standalone or embedded in a larger application,
    // so the root object is created only when it is absent.
    if (!window.zato) {
        window.zato = {};
    }

    zato.mapper = {};

    zato.mapper.config = {

        // Artifact format
        artifactVersion: 1,
        defaultName: 'New mapping',
        defaultDescription: '',

        // Browser storage keys
        artifactStorageKey: 'zato-mapper-artifact',
        namedSchemasStorageKey: 'zato-mapper-named-schemas',
        activeTabStorageKey: 'zato-mapper-active-tab',

        // Undo and redo depth
        undoLimit: 200,

        // Serialization
        jsonIndent: 2,

        // Tabs
        tabs: [
            {name: 'design', label: 'Design'},
            {name: 'code', label: 'Code'},
            {name: 'tests', label: 'Tests'},
            {name: 'import', label: 'Import'}
        ],
        defaultTab: 'design',

        // The active-tab markers - the mapper's own class and the
        // dashboard kit's class toggle together.
        tabActiveClass: 'mapper-tab-active dashboard-tab-active',
        subtabActiveClass: 'mapper-subtab-active dashboard-tab-active',

        // The side Design-tab area - the mappings and the live preview
        designSideTabStorageKey: 'zato-mapper-design-side-tab',
        designSideDefaultTab: 'mappings',

        // Scaffolding placeholders per leaf type
        scaffoldValues: {
            string: '????',
            number: 0,
            boolean: false,
            unknown: null
        },

        // Scaffolding placeholders per string format hint
        scaffoldFormatValues: {
            date: '2026-01-01',
            datetime: '2026-01-01T00:00:00Z',
            time: '12:00:00'
        },

        // Export file name for the artifact download
        exportFileName: 'mapping.json',

        // Panel split - default, bounds and keyboard step, all in percent
        designSplitStorageKey: 'zato-mapper-design-split',
        splitDefaultPercent: 50,
        splitMinPercent: 15,
        splitMaxPercent: 85,
        splitKeyboardStepPercent: 2,

        // The split between the maps area and the side area
        designSideSplitStorageKey: 'zato-mapper-design-side-split',
        designSideSplitDefaultPercent: 62,

        // The split between the preview's input and output panes
        previewSplitStorageKey: 'zato-mapper-preview-split',
        previewSplitDefaultPercent: 50,

        // Sides a schema or sample may belong to
        sides: ['source', 'target'],

        // The examples a brand-new mapping starts with, so the page is
        // never blank - they disappear as soon as anything else is pasted
        // or restored from browser storage.
        defaultExamples: {
            source: {
                name: 'source-example-1',
                payload: {
                    customer: 'ACME',
                    quantity: 2,
                    unit_price: 10.5,
                    notes: '',
                    lines: [
                        {sku: 'AA-11', quantity: 2},
                        {sku: 'BB-22', quantity: 5}
                    ]
                }
            },
            target: {
                name: 'target-example-1',
                payload: {
                    invoice_number: 'INV-100',
                    buyer: 'ACME',
                    amount: 125.5,
                    items: [
                        {code: 'AA-11', count: 2}
                    ]
                }
            }
        },

        // Preview
        activeSampleStorageKey: 'zato-mapper-active-sample',
        previewEmptyValueLabel: '-',

        // How long a page notice stays on screen
        noticeAutoHideMs: 8000,

        // Autocomplete
        autocompleteMaxItems: 8,

        // The tree filters, in the order the Options menus list them,
        // and the menu group they sit under
        treeFilterGroupLabel: 'Filter',
        treeFilters: [
            {name: 'all', label: 'All'},
            {name: 'mapped', label: 'Mapped'},
            {name: 'unmapped', label: 'Unmapped'},
            {name: 'required', label: 'Required'},
            {name: 'invalid', label: 'Invalid'}
        ],
        defaultTreeFilter: 'all',

        // What the search counter says when nothing matches
        // The per-column Options menu - each item names an action
        // the page dispatches on for that column's side.
        schemaColumnMenu: [
            {group: 'Tree', items: [
                {name: 'collapse-all', label: 'Collapse all'},
                {name: 'expand-mapped', label: 'Expand mapped'}
            ]}
        ],

        // Values treated as empty by the omit-if-empty and default semantics
        // are undefined, null and the empty string.

        // Operator chips offered by the expression builder
        builderOperators: ['+', '-', '*', '/', '&', '=', '!=', '>', '<'],

        // The categories the expression functions group under, in the
        // order pickers and autocomplete list them
        functionCategories: [
            {name: 'string', label: 'String'},
            {name: 'numeric', label: 'Numeric'},
            {name: 'date', label: 'Date'},
            {name: 'list', label: 'List'},
            {name: 'object', label: 'Object'},
            {name: 'logic', label: 'Logic'}
        ],

        // The expression functions offered in autocomplete and as builder chips
        functionReference: [
            {name: '$string', doc: 'Casts the argument to a string', category: 'string'},
            {name: '$uppercase', doc: 'Returns the string in upper case', category: 'string'},
            {name: '$lowercase', doc: 'Returns the string in lower case', category: 'string'},
            {name: '$trim', doc: 'Trims surrounding whitespace', category: 'string'},
            {name: '$length', doc: 'Returns the length of a string', category: 'string'},
            {name: '$substring', doc: 'Returns part of a string', category: 'string'},
            {name: '$replace', doc: 'Replaces occurrences within a string', category: 'string'},
            {name: '$split', doc: 'Splits a string into a list', category: 'string'},
            {name: '$join', doc: 'Joins a list into one string', category: 'string'},
            {name: '$contains', doc: 'Whether a string contains a pattern', category: 'string'},
            {name: '$pad', doc: 'Pads a string to a width', category: 'string'},
            {name: '$number', doc: 'Casts the argument to a number', category: 'numeric'},
            {name: '$sum', doc: 'Sums a list of numbers', category: 'numeric'},
            {name: '$max', doc: 'Returns the largest number of a list', category: 'numeric'},
            {name: '$min', doc: 'Returns the smallest number of a list', category: 'numeric'},
            {name: '$average', doc: 'Returns the average of a list', category: 'numeric'},
            {name: '$round', doc: 'Rounds a number', category: 'numeric'},
            {name: '$abs', doc: 'Returns the absolute value', category: 'numeric'},
            {name: '$floor', doc: 'Rounds a number down', category: 'numeric'},
            {name: '$ceil', doc: 'Rounds a number up', category: 'numeric'},
            {name: '$now', doc: 'The current timestamp as a string', category: 'date'},
            {name: '$millis', doc: 'The current timestamp in milliseconds', category: 'date'},
            {name: '$fromMillis', doc: 'Formats milliseconds as a timestamp', category: 'date'},
            {name: '$toMillis', doc: 'Parses a timestamp into milliseconds', category: 'date'},
            {name: '$count', doc: 'Counts the items of a list', category: 'list'},
            {name: '$map', doc: 'Applies a function to every item', category: 'list'},
            {name: '$filter', doc: 'Keeps the items a function accepts', category: 'list'},
            {name: '$reduce', doc: 'Folds a list into one value', category: 'list'},
            {name: '$sort', doc: 'Sorts a list', category: 'list'},
            {name: '$distinct', doc: 'Removes duplicates from a list', category: 'list'},
            {name: '$keys', doc: 'Returns the keys of an object', category: 'object'},
            {name: '$lookup', doc: 'Returns the value of a key in an object', category: 'object'},
            {name: '$merge', doc: 'Merges a list of objects', category: 'object'},
            {name: '$boolean', doc: 'Casts the argument to a boolean', category: 'logic'},
            {name: '$not', doc: 'Negates a boolean', category: 'logic'},
            {name: '$exists', doc: 'Whether a value is present', category: 'logic'}
        ]
    };

})(jQuery);
