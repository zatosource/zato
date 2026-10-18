// MCP gateway wizard - the data masking logic of masking-sets.js, data-masking.js,
// masking-popover.js and masking-search.js, run in a vm context with a stub of the jQuery
// namespace, of the micro-forms engine and of the document.
//
// Usage: node mcp-wizard-masking.js <the mcp-wizard static directory>
// The industry sets arrive as JSON on standard input, in the form the page embeds them.
// Every assertion that fails is printed and the process exits with status 1.

'use strict';

var assert = require('assert');
var fs = require('fs');
var path = require('path');
var vm = require('vm');

// ////////////////////////////////////////////////////////////////////////

var config = {
    scriptNames: ['masking-sets.js', 'data-masking.js', 'masking-popover.js', 'masking-search.js'],
    setsScriptId: 'mcp-wizard-masking-sets',
    stateScriptId: 'mcp-wizard-masking-state'
};

// ////////////////////////////////////////////////////////////////////////

var buildContext = function(setsText, stateText) {

    var embedded = {};
    embedded[config.setsScriptId] = setsText;
    embedded[config.stateScriptId] = stateText;

    var wizard = {
        maskingSets: {},
        dataMasking: {},
        maskingPopover: {},
        searchBox: {},
        forms: {
            descriptors: {},
            registerKind: function() {}
        },
        review: {
            setSummary: function() {}
        }
    };

    var jQuery = function() {
        var out = {on: function() {}};
        return out;
    };

    jQuery.fn = {zato: {gateway: {mcp: {wizard: wizard}}}};

    var documentStub = {
        getElementById: function(elementId) {
            var out = {textContent: embedded[elementId]};
            return out;
        }
    };

    var out = vm.createContext({jQuery: jQuery, document: documentStub, JSON: JSON});
    return out;
};

// ////////////////////////////////////////////////////////////////////////

var loadWizard = function(staticDirectory, setsText, state) {

    var context = buildContext(setsText, JSON.stringify(state));

    for(var scriptIdx = 0; scriptIdx < config.scriptNames.length; scriptIdx++) {
        var scriptPath = path.join(staticDirectory, config.scriptNames[scriptIdx]);
        vm.runInContext(fs.readFileSync(scriptPath, 'utf8'), context, {filename: scriptPath});
    }

    var wizard = context.jQuery.fn.zato.gateway.mcp.wizard;

    wizard.maskingSets.init();
    wizard.dataMasking.init();

    return wizard;
};

// ////////////////////////////////////////////////////////////////////////

// The popover with a working copy of the answers, as the micro-form gives it when it opens.
var loadPopover = function(staticDirectory, setsText, setNames, excluded) {

    var state = emptyState();
    state.sets = setNames;
    state.excluded = excluded;

    var popover = loadWizard(staticDirectory, setsText, state).maskingPopover;
    popover.working = popover._copyState(state);

    return popover;
};

// ////////////////////////////////////////////////////////////////////////

// The names of the sets listing a field, compared without regard to case, in the order of the sets.
var setsListing = function(sets, fieldName) {

    var out = [];

    for(var setIdx = 0; setIdx < sets.length; setIdx++) {

        var lowered = sets[setIdx].fields.map(function(name) { return name.toLowerCase(); });

        if(lowered.indexOf(fieldName.toLowerCase()) !== -1) {
            out.push(sets[setIdx].name);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

var maskingSetsSubtract = function(fieldList, names) {

    var lowered = names.map(function(name) { return name.toLowerCase(); });

    var out = fieldList.filter(function(fieldName) { return lowered.indexOf(fieldName.toLowerCase()) === -1; });
    return out;
};

// ////////////////////////////////////////////////////////////////////////

var emptyState = function() {
    var out = {sets: [], excluded: [], customFields: [], isCustomEnabled: true, requestHook: '', responseHook: ''};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Plain copies, so arrays built in the vm context compare equal to arrays built here.
var plain = function(value) {
    var out = JSON.parse(JSON.stringify(value));
    return out;
};

// ////////////////////////////////////////////////////////////////////////

var buildCases = function(staticDirectory, setsText) {

    var sets = JSON.parse(setsText);
    var bankingFields = null;

    for(var setIdx = 0; setIdx < sets.length; setIdx++) {
        if(sets[setIdx].name === 'banking') {
            bankingFields = sets[setIdx].fields;
        }
    }

    var cases = {};

    cases.theSetsAreTheEmbeddedOnes = function() {
        var wizard = loadWizard(staticDirectory, setsText, emptyState());
        assert.deepStrictEqual(plain(wizard.maskingSets.all()), sets);
    };

    cases.holdsComparesWithoutRegardToCase = function() {
        var maskingSets = loadWizard(staticDirectory, setsText, emptyState()).maskingSets;
        assert.strictEqual(maskingSets.holds(['customer', 'iban'], 'IBAN'), true);
        assert.strictEqual(maskingSets.holds(['Customer'], 'customer'), true);
        assert.strictEqual(maskingSets.holds(['customer'], 'customers'), false);
    };

    cases.mergeAppendsOnlyNewNames = function() {
        var maskingSets = loadWizard(staticDirectory, setsText, emptyState()).maskingSets;
        var out = maskingSets.merge(['iban', 'bic'], ['BIC', 'Customer', 'customer', 'swift']);
        assert.deepStrictEqual(plain(out), ['iban', 'bic', 'Customer', 'swift']);
    };

    cases.mergeLeavesItsInputAlone = function() {
        var maskingSets = loadWizard(staticDirectory, setsText, emptyState()).maskingSets;
        var original = ['iban'];
        var merged = maskingSets.merge(original, ['bic']);
        assert.deepStrictEqual(plain(original), ['iban']);
        assert.deepStrictEqual(plain(merged), ['iban', 'bic']);
    };

    cases.subtractRemovesInAnyCase = function() {
        var maskingSets = loadWizard(staticDirectory, setsText, emptyState()).maskingSets;
        var out = maskingSets.subtract(['iban', 'BIC', 'customer'], ['bic', 'CUSTOMER']);
        assert.deepStrictEqual(plain(out), ['iban']);
    };

    cases.unionHoldsEachFieldOnce = function() {
        var maskingSets = loadWizard(staticDirectory, setsText, emptyState()).maskingSets;
        var out = maskingSets.union(['banking', 'banking']);
        assert.deepStrictEqual(plain(out), bankingFields);
    };

    cases.maskedFieldsOfNothingIsEmpty = function() {
        var dataMasking = loadWizard(staticDirectory, setsText, emptyState()).dataMasking;
        assert.deepStrictEqual(plain(dataMasking.maskedFields(dataMasking.state)), []);
    };

    cases.maskedFieldsLeavesOutTheExcluded = function() {
        var state = emptyState();
        state.sets = ['banking'];
        state.excluded = ['IBAN'];

        var dataMasking = loadWizard(staticDirectory, setsText, state).dataMasking;
        var out = plain(dataMasking.maskedFields(dataMasking.state));

        assert.strictEqual(out.indexOf('iban'), -1);
        assert.strictEqual(out.length, bankingFields.length - 1);
    };

    cases.maskedFieldsAddsTheCustomFields = function() {
        var state = emptyState();
        state.sets = ['banking'];
        state.customFields = ['Loyalty_Id', 'IBAN'];

        var dataMasking = loadWizard(staticDirectory, setsText, state).dataMasking;
        var out = plain(dataMasking.maskedFields(dataMasking.state));

        assert.strictEqual(out[out.length - 1], 'Loyalty_Id');
        assert.strictEqual(out.length, bankingFields.length + 1);
    };

    cases.maskedFieldsSkipsCustomFieldsSwitchedOff = function() {
        var state = emptyState();
        state.customFields = ['loyalty_id'];
        state.isCustomEnabled = false;

        var dataMasking = loadWizard(staticDirectory, setsText, state).dataMasking;
        assert.deepStrictEqual(plain(dataMasking.maskedFields(dataMasking.state)), []);
    };

    cases.theStoredStateIsRestored = function() {
        var state = emptyState();
        state.sets = ['healthcare', 'banking'];
        state.excluded = ['iban'];
        state.customFields = ['loyalty_id'];
        state.isCustomEnabled = false;

        var dataMasking = loadWizard(staticDirectory, setsText, state).dataMasking;
        var restored = plain(dataMasking.state);

        assert.deepStrictEqual(restored.sets, ['healthcare', 'banking']);
        assert.deepStrictEqual(restored.excluded, ['iban']);
        assert.deepStrictEqual(restored.customFields, ['loyalty_id']);
        assert.strictEqual(restored.isCustomEnabled, false);
    };

    cases.theSummaryNamesTheSetsAndTheCount = function() {
        var state = emptyState();
        state.sets = ['banking'];
        state.customFields = ['loyalty_id'];

        var dataMasking = loadWizard(staticDirectory, setsText, state).dataMasking;
        var label = dataMasking.config.labels;
        var expected = 'Banking (' + bankingFields.length + '), ' + label.custom + ' (1)';

        assert.strictEqual(dataMasking.summary(), expected);
    };

    cases.parseKeepsEachNameOnce = function() {
        var dataMasking = loadWizard(staticDirectory, setsText, emptyState()).dataMasking;
        var out = dataMasking.parse('  iban \n\nbic\niban\n');
        assert.deepStrictEqual(plain(out), ['iban', 'bic']);
    };

    cases.parseKeepsEachNameOnceInAnyCase = function() {
        var dataMasking = loadWizard(staticDirectory, setsText, emptyState()).dataMasking;
        var out = dataMasking.parse('iban\nIBAN\nIban\nbic');
        assert.deepStrictEqual(plain(out), ['iban', 'bic']);
    };

    cases.setsListingNamesEverySetListingTheField = function() {
        var maskingSets = loadWizard(staticDirectory, setsText, emptyState()).maskingSets;
        assert.deepStrictEqual(plain(maskingSets.setsListing('EMAIL')), setsListing(sets, 'email'));
        assert.deepStrictEqual(plain(maskingSets.setsListing('iban')), setsListing(sets, 'iban'));
    };

    cases.noSetListsAFieldTwice = function() {
        for(var setIdx = 0; setIdx < sets.length; setIdx++) {
            var lowered = sets[setIdx].fields.map(function(fieldName) { return fieldName.toLowerCase(); });
            assert.strictEqual(new Set(lowered).size, lowered.length, sets[setIdx].name);
        }
    };

    cases.aFieldIsMaskedWhicheverPickedSetListsIt = function() {
        var popover = loadPopover(staticDirectory, setsText, ['common'], []);
        assert.strictEqual(popover.isMasked('email'), true);
        assert.strictEqual(popover.isMasked('EMAIL'), true);
        assert.strictEqual(popover.isMasked('iban'), false);
    };

    cases.anExclusionCoversEverySetListingTheField = function() {
        var popover = loadPopover(staticDirectory, setsText, ['common', 'banking'], []);
        popover.toggleField('banking', 'email');

        assert.strictEqual(popover.isMasked('email'), false);
        assert.deepStrictEqual(plain(popover.working.sets), ['common', 'banking']);
        assert.deepStrictEqual(plain(popover.working.excluded), ['email']);
    };

    cases.aFieldOfASetNotPickedPicksTheSetWithThatFieldAlone = function() {
        var popover = loadPopover(staticDirectory, setsText, ['common'], []);
        popover.toggleField('banking', 'iban');

        assert.strictEqual(popover.isPicked('banking'), true);
        assert.strictEqual(popover.isMasked('iban'), true);
        assert.strictEqual(popover.isMasked('email'), true);
        assert.strictEqual(popover.isMasked('bic'), false);
    };

    cases.aFieldAnotherPickedSetListsLeavesTheSetUnpicked = function() {
        var popover = loadPopover(staticDirectory, setsText, ['common'], ['email']);
        popover.toggleField('banking', 'email');

        assert.strictEqual(popover.isMasked('email'), true);
        assert.strictEqual(popover.isPicked('banking'), false);
        assert.deepStrictEqual(plain(popover.working.excluded), []);
    };

    cases.lettingASetGoKeepsTheExclusionsOtherSetsNeed = function() {
        var popover = loadPopover(staticDirectory, setsText, ['common', 'banking'], ['email', 'iban']);
        popover.setPicked('banking', false);

        assert.deepStrictEqual(plain(popover.working.sets), ['common']);
        assert.deepStrictEqual(plain(popover.working.excluded), ['email']);
        assert.strictEqual(popover.isMasked('email'), false);
    };

    cases.pickingASetClearsTheExclusionsOfItsFields = function() {
        var popover = loadPopover(staticDirectory, setsText, ['common'], ['email', 'last_ip']);
        popover.setPicked('banking', true);

        assert.strictEqual(popover.isMasked('email'), true);
        assert.deepStrictEqual(plain(popover.working.excluded), maskingSetsSubtract(['last_ip'], bankingFields));
    };

    cases.aSetLeftWithNoFieldIsLetGo = function() {
        var excluded = bankingFields.filter(function(fieldName) { return fieldName !== 'bic'; });
        var popover = loadPopover(staticDirectory, setsText, ['banking'], excluded);
        popover.toggleField('banking', 'bic');

        assert.strictEqual(popover.isPicked('banking'), false);
    };

    cases.theSearchTermsSplitOnSpacesAndUnderscores = function() {
        var search = loadPopover(staticDirectory, setsText, [], []).search;
        assert.deepStrictEqual(plain(search.terms('  Last_IP  address ')), ['last', 'ip', 'address']);
        assert.deepStrictEqual(plain(search.terms('   ')), []);
    };

    cases.aFieldMatchesWhenItHoldsEveryTerm = function() {
        var search = loadPopover(staticDirectory, setsText, [], []).search;
        assert.strictEqual(search.matches('last_ip', ['last', 'ip']), true);
        assert.strictEqual(search.matches('Last_IP', ['last', 'ip']), true);
        assert.strictEqual(search.matches('ip_address', ['last', 'ip']), false);
        assert.strictEqual(search.matches('anything', []), true);
    };

    cases.theSearchKeepsTheOrderOfTheFields = function() {
        var search = loadPopover(staticDirectory, setsText, [], []).search;
        assert.deepStrictEqual(plain(search.matching(['remote_ip', 'email', 'client_ip'], ['ip'])), ['remote_ip', 'client_ip']);
    };

    cases.theResultTextNamesTheFieldsAndTheSets = function() {
        var search = loadPopover(staticDirectory, setsText, [], []).search;
        assert.strictEqual(search.resultText(0, 0), 'No fields');
        assert.strictEqual(search.resultText(1, 1), '1 field in 1 set');
        assert.strictEqual(search.resultText(21, 15), '21 fields in 15 sets');
    };

    cases.commonListsTheAddressesOfAClient = function() {
        var commonFields = sets.filter(function(set) { return set.name === 'common'; })[0].fields;
        var expected = ['last_ip', 'ip', 'ip_address', 'ipaddress', 'ip_addresses', 'client_ip', 'remote_ip', 'remote_addr',
            'source_ip'];

        for(var fieldIdx = 0; fieldIdx < expected.length; fieldIdx++) {
            assert.notStrictEqual(commonFields.indexOf(expected[fieldIdx]), -1, expected[fieldIdx]);
        }
    };

    return cases;
};

// ////////////////////////////////////////////////////////////////////////

var main = function() {

    var staticDirectory = process.argv[2];
    var setsText = fs.readFileSync(0, 'utf8');

    var cases = buildCases(staticDirectory, setsText);
    var failures = [];
    var names = Object.keys(cases);

    for(var nameIdx = 0; nameIdx < names.length; nameIdx++) {

        var name = names[nameIdx];

        try {
            cases[name]();
            console.log('ok ' + name);
        }
        catch(error) {
            failures.push(name);
            console.log('not ok ' + name + '\n' + error.stack);
        }
    }

    if(failures.length > 0) {
        process.exit(1);
    }
};

main();
