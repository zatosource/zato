// A demo of the shared progress panel - the Run demo button plays a made-up switch of the environment
// through the panel under the actions row, with a live state, a progress bar and lines of each kind.

$.fn.zato.envRepoDemo = {};

$.fn.zato.envRepoDemo.config = {
    theme: 'dark',
    source: 'zato-env-repo',
    stepDelay: 450,
    steps: [
        {text: 'Request received - switch to zatosource/zato-environment at main', kind: null},
        {text: 'Checking access with the deploy key', kind: null},
        {text: 'git ls-remote --heads git@github.com:zatosource/zato-environment.git', kind: null},
        {text: '5e1c0d5a4d9b1f4a3c2b1a0f9e8d7c6b5a4f3e2d\trefs/heads/main', kind: null},
        {text: '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b\trefs/heads/develop', kind: null},
        {text: 'Access confirmed, 2 branches found', kind: 'ok'},
        {text: 'Fetching origin', kind: null},
        {text: 'remote: Enumerating objects: 148, done.', kind: null},
        {text: 'remote: Counting objects: 100% (148/148), done.', kind: null},
        {text: 'remote: Compressing objects: 100% (91/91), done.', kind: null},
        {text: 'Receiving objects: 100% (148/148), 41.20 KiB | 2.06 MiB/s, done.', kind: null},
        {text: 'Resolving deltas: 100% (52/52), done.', kind: null},
        {text: 'Checking out main at 5e1c0d5', kind: null},
        {text: 'Switched to branch main', kind: 'ok'},
        {text: 'Linking /opt/zato/env/project -> /opt/zato/env/repo/env', kind: null},
        {text: 'warning: env.ini already exists, keeping the current file', kind: 'error'},
        {text: 'Reloading services', kind: null},
        {text: 'Deployed 6 services from 3 modules', kind: 'ok'},
        {text: 'Switch complete', kind: 'ok'},
    ],
};

$.fn.zato.envRepoDemo.state = {
    log: null,
    timer: null,
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepoDemo.init = function() {

    var config = $.fn.zato.envRepoDemo.config;

    $.fn.zato.envRepoDemo.state.log = progressLog.create({
        container: document.getElementById('progress-log'),
        theme: config.theme,
        source: config.source,
        isHidden: true,
        hasProgressBar: true,
    });

    $('#demo-button').on('click', $.fn.zato.envRepoDemo.run);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepoDemo.run = function() {

    var state = $.fn.zato.envRepoDemo.state;

    if(state.timer) {
        clearTimeout(state.timer);
    }

    state.log.clear();
    state.log.show();
    state.log.setState('live');
    state.log.setProgress(0);

    $.fn.zato.envRepoDemo.play(0);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepoDemo.play = function(index) {

    var config = $.fn.zato.envRepoDemo.config;
    var state = $.fn.zato.envRepoDemo.state;
    var steps = config.steps;

    if(index === steps.length) {
        state.log.setState('done');
        state.timer = null;
        return;
    }

    var step = steps[index];

    state.log.append({text: step.text, kind: step.kind, time: new Date()});
    state.log.setProgress((index + 1) / steps.length);

    // Lines that report the outcome of a step take a moment longer, as they would in a real run.
    var delay = step.kind === null ? config.stepDelay : config.stepDelay * 2;

    state.timer = setTimeout(function() {
        $.fn.zato.envRepoDemo.play(index + 1);
    }, delay);
};

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.envRepoDemo.init();
});
