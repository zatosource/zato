'use strict';

// The jsdom smoke: every dashboard screen, rendered through the Django
// test client, boots in jsdom with its fetch calls bridged to a live
// test-owned server, and the view objects are then driven directly -
// so a broken template id, a script that dies at load or a payload
// shape the JavaScript no longer understands all fail the build.
//
// Arguments, in order:
//   1. the directory with the rendered pages, one <name>.html per screen
//   2. the base url of the test-owned server, e.g. http://127.0.0.1:40123
//   3. the cookie header - the session and the CSRF cookie
//   4. the webapp static root on disk (serves /static/webapp/...)
//   5. the dashboard static root on disk (serves /static/rule-engine/...)

const fs = require('fs');
const path = require('path');
const {JSDOM, VirtualConsole, requestInterceptor} = require('jsdom');

const pagesDir = process.argv[2];
const serverBase = process.argv[3];
const cookieHeader = process.argv[4];
const webappStaticRoot = process.argv[5];
const dashboardStaticRoot = process.argv[6];

// How long a screen may take to settle after its scripts run
const settleTimeoutMs = 10000;
const settlePollMs = 25;

// ////////////////////////////////////////////////////////////////////////

// Scripts and stylesheets resolve from disk, exactly the files Django
// would serve under /static/ - no network is involved.
const contentTypes = {
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.svg': 'image/svg+xml',
    '.woff2': 'font/woff2',
};

const diskInterceptor = requestInterceptor((request) => {
    const urlPath = new URL(request.url).pathname;
    let filePath = null;

    if (urlPath.startsWith('/static/webapp/')) {
        filePath = path.join(webappStaticRoot, urlPath.slice('/static/webapp/'.length));
    }
    if (urlPath.startsWith('/static/rule-engine/')) {
        filePath = path.join(dashboardStaticRoot, urlPath.slice('/static/rule-engine/'.length));
    }

    if (filePath === null) {
        return new Response('only /static/ resources load in this harness: ' + urlPath, {status: 404});
    }

    const contentType = contentTypes[path.extname(filePath)];
    return new Response(fs.readFileSync(filePath), {headers: {'Content-Type': contentType}});
});

// ////////////////////////////////////////////////////////////////////////

let failures = 0;

function check(label, condition) {
    if (condition) {
        console.log('ok   ' + label);
    } else {
        failures += 1;
        console.log('FAIL ' + label);
    }
}

// Polls until the predicate holds, so the boot sequence's fetch chains
// have time to land before the screen is inspected.
function waitFor(predicate) {
    return new Promise((resolve) => {
        const started = Date.now();
        const timer = setInterval(() => {
            if (predicate()) {
                clearInterval(timer);
                resolve(true);
                return;
            }
            if (Date.now() - started > settleTimeoutMs) {
                clearInterval(timer);
                resolve(false);
            }
        }, settlePollMs);
    });
}

// ////////////////////////////////////////////////////////////////////////

// Boots one rendered page in jsdom: scripts run for real, fetch goes to
// the live test server with the signed-in session, and page errors are
// collected instead of crashing the harness.
async function bootPage(fileName, urlPath) {
    const html = fs.readFileSync(path.join(pagesDir, fileName), 'utf8');
    const pageErrors = [];

    const virtualConsole = new VirtualConsole();
    virtualConsole.on('jsdomError', (error) => { pageErrors.push(String(error.message || error)); });

    const dom = new JSDOM(html, {
        url: serverBase + urlPath,
        runScripts: 'dangerously',
        resources: {interceptors: [diskInterceptor]},
        pretendToBeVisual: true,
        virtualConsole: virtualConsole,
    });

    // The bridge: relative fetches from the page land on the live server
    // under the signed-in session, exactly as a browser would send them
    dom.window.fetch = function(url, options) {
        options = options || {};
        const headers = Object.assign({}, options.headers, {Cookie: cookieHeader});
        return fetch(serverBase + url, {method: options.method || 'GET', headers: headers, body: options.body});
    };

    // The page's scripts are external resources, so the load event fires
    // only once every one of them has run
    await new Promise((resolve) => {
        dom.window.addEventListener('load', resolve);
    });

    return {window: dom.window, pageErrors: pageErrors};
}

// ////////////////////////////////////////////////////////////////////////

// One entry per screen: the page file, its url, a marker the seeded data
// must put on the screen, and an optional direct drive of the view object.
const screens = [
    {
        file: 'rulesets.html',
        urlPath: '/rulesets/',
        // The seeded ruleset lands in the list pane
        settled: (window) => window.document.getElementById('rulesets-list').textContent.includes('Loans'),
        drive: async (window) => {
            // The preview pane is driven directly for the seeded ruleset
            const model = window.rulesetsModel;
            check('rulesets: the model holds the seeded ruleset',
                model.rulesets.some((item) => item.name === 'Loans'));

            // The filter bar is driven the way a hand would: focus, then tick the first facet
            const view = window.rulesetsView;
            window.document.getElementById('rulesets-search').focus();

            check('rulesets: the filter bar offers its facets',
                window.document.getElementById('rulesets-suggest').textContent.includes('status'));

            view.pick(0);
            check('rulesets: ticking a facet chooses it', view.chosen.length === 1);

            const narrowed = await waitFor(
                () => window.document.getElementById('rulesets-count').textContent.includes(' of '));
            check('rulesets: the count reads as the matching part of the whole', narrowed);

            view.pick(0);
            const unticked = await waitFor(() => view.chosen.length === 0);
            check('rulesets: ticking the same facet again lets it go', unticked);

            view.clearAll();
            const cleared = await waitFor(
                () => !window.document.getElementById('rulesets-count').textContent.includes(' of '));
            check('rulesets: clearing takes the count back to every set', cleared);
        },
    },
    {
        file: 'editor.html',
        urlPath: '/editor/',
        // The seeded rule opens in the sentence editor
        settled: (window) => window.document.getElementById('editor-area').textContent.includes('credit_score'),
        drive: (window) => {
            const rule = window.editorModel.rule;
            check('editor: the rule model carries the seeded condition',
                rule.conditions.some((condition) => condition.subject === 'credit_score'));
        },
    },
    {
        file: 'tables.html',
        urlPath: '/tables/',
        // The seeded decision table renders its grid
        settled: (window) => window.document.getElementById('table-grid-area').textContent.includes('credit_score'),
        drive: async (window) => {
            check('tables: the table model carries the seeded columns',
                window.tableModel.table.columns.length === 3);

            // The cell grammar lives on the server alone, so the sentence bar
            // only speaks once the validation has answered with its readings
            const read = await waitFor(() => Object.keys(window.tableModel.readings).length > 0);
            check('tables: the server answers with how every cell reads', read);

            window.tableView.selectColumn('1');
            const sentence = window.document.getElementById('table-sentence-bar').textContent;
            check('tables: the sentence bar speaks the range the server read, saw ' + JSON.stringify(sentence),
                sentence.includes('between 700 and 850'));
        },
    },
    {
        file: 'tests.html',
        urlPath: '/tests/',
        // The seeded suite with its scenarios is on screen
        settled: (window) => window.document.getElementById('test-set-list').textContent.includes('High score gets the rate'),
        drive: (window) => {
            check('tests: the suite model carries both scenarios', window.testModel.suite.scenarios.length === 2);
        },
    },
    {
        file: 'versions.html',
        urlPath: '/versions/',
        // The two seeded versions land on the timeline with their comments
        settled: (window) => window.document.body.textContent.includes('Lower the bar'),
        drive: (window) => {
            check('versions: the timeline holds both versions', window.versionsModel.versions.length === 2);
        },
    },
    {
        file: 'log.html',
        urlPath: '/decision-log/',
        // The seeded decisions land in the list with their business keys
        settled: (window) => window.document.getElementById('log-list').textContent.includes('Mary Miller'),
        drive: async (window) => {
            // The search filter is driven directly: one key stays, the other
            // goes, once the debounce behind the keystrokes has fired
            window.logView.setSearch('Mary');

            const filtered = await waitFor(
                () => !window.document.getElementById('log-list').textContent.includes('James Carter'));

            check('log: setSearch filters the other decision out', filtered);
            check('log: setSearch keeps the matching decision',
                window.document.getElementById('log-list').textContent.includes('Mary Miller'));
        },
    },
    {
        file: 'vocabulary.html',
        urlPath: '/vocabulary/',
        // The seeded vocabulary tree is on screen with its phrases
        settled: (window) => window.document.body.textContent.includes('credit score'),
        drive: (window) => {
            check('vocabulary: the model holds both seeded entities', window.vocabulary.entities.length === 2);
        },
    },
    {
        file: 'notifications.html',
        urlPath: '/notifications/',
        // The seeded ruleset is the destinations context
        settled: (window) => window.document.body.textContent.includes('Loans'),
        drive: (window) => {
            check('notifications: the model opens on the seeded ruleset',
                window.notifyModel.rulesetName === 'Loans');
        },
    },
];

// ////////////////////////////////////////////////////////////////////////

async function main() {

    for (const screen of screens) {
        const {window, pageErrors} = await bootPage(screen.file, screen.urlPath);

        const isSettled = await waitFor(() => screen.settled(window));
        check(screen.file + ': the seeded data is on screen', isSettled);
        check(screen.file + ': no page errors, saw ' + JSON.stringify(pageErrors), pageErrors.length === 0);

        // A driver may have to wait for a debounce of its own, so every one
        // of them is awaited
        if (isSettled) {
            await screen.drive(window);
        }
    }

    if (failures > 0) {
        console.log(failures + ' jsdom check(s) failed');
        process.exit(1);
    }
    console.log('all jsdom checks passed');

    // The windows stay open on purpose: the screens keep debounced server
    // checks in flight and closing them mid-flight would tear the document
    // from under a callback. The explicit exit ends everything at once.
    process.exit(0);
}

main().then(() => {}, (error) => {
    console.log('the harness itself failed: ' + (error.stack || error));
    process.exit(1);
});
