// The repositories the GitHub App may read - the list the address field offers, the one filled in on its own,
// and the hint by the Connect button that leads to a new repository from the template.
// ////////////////////////////////////////////////////////////////////////

// The repositories the App may read are in the page already, newest first, and the one alone is in the field already too.
// Right after the installation, the newest one is connected if a repository was just created, and otherwise several
// are left for the user to pick from.
$.fn.zato.envRepo.pickRepo = function(isInstalledNow) {

    const repos = $.fn.zato.envRepo.readRepoList();

    if(!isInstalledNow || !repos.length) {
        return;
    }

    if($.fn.zato.envRepo.isCreating(true)) {
        $('#repo-url').val('https://github.com/' + repos[0]);
        $.fn.zato.envRepo.handleConnect();
    }
    else {
        $('#repo-url').focus();
    }
};

// ////////////////////////////////////////////////////////////////////////

// The repositories as the page came with them, without the address prefix.
$.fn.zato.envRepo.readRepoList = function() {

    const out = [];

    $('#repo-list option').each(function() {
        out.push($(this).attr('value').replace('https://github.com/', ''));
    });

    $.fn.zato.envRepo.state.knownRepos = out;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The hint by the Connect button, with the link to a new repository from the template, there as long as the field is empty.
$.fn.zato.envRepo.initHint = function() {

    const config = $.fn.zato.envRepo.config;
    const button = $('#action-button');

    const link = $('<a></a>').attr('href', button.data('new-repo-url')).attr('target', '_blank').attr('rel', 'noopener')
        .text(button.data('new-repo-label'));

    // The repository created on GitHub is the one to connect to once the browser is back here, with or without
    // the App's two pages in between.
    link.on('click', function() {
        window.sessionStorage.setItem(config.creatingKey, '1');
        $.fn.zato.envRepo.updateHint();
    });

    const content = $('<span class="env-repo-hint"></span>').text(button.data('new-repo-hint')).append($('<br>')).append(link);

    $.fn.zato.envRepo.state.hint = tippy(button[0], {
        content: content[0],
        placement: config.hintPlacement,
        theme: config.hintTheme,
        arrow: true,
        interactive: true,
        trigger: 'manual',
        hideOnClick: false,
        duration: [200, 0],
        appendTo: document.body,
    });
};

// ////////////////////////////////////////////////////////////////////////

// Returns whether a repository is being created on GitHub right now, and forgets it if asked to.
$.fn.zato.envRepo.isCreating = function(shouldForget) {

    const config = $.fn.zato.envRepo.config;
    const out = window.sessionStorage.getItem(config.creatingKey) === '1';

    if(shouldForget) {
        window.sessionStorage.removeItem(config.creatingKey);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// With the App installed, the tab regaining focus while a repository is being created on GitHub looks the list up
// again, and a repository not in it before is the new one, filled in and connected.
$.fn.zato.envRepo.handleFocus = function() {

    const config = $.fn.zato.envRepo.config;
    const state = $.fn.zato.envRepo.state;

    if(!$.fn.zato.envRepo.isCreating(false) || state.appState !== config.appStateInstalled) {
        return;
    }

    if($('#repo-url').val().trim()) {
        return;
    }

    const known = state.knownRepos || $.fn.zato.envRepo.readRepoList();

    $.fn.zato.envRepo.fetchRepos(function(repos) {

        $.fn.zato.envRepo.fillRepoList(repos);

        for(let idx = 0; idx < repos.length; idx++) {
            if(known.indexOf(repos[idx]) === -1) {
                $.fn.zato.envRepo.isCreating(true);
                $('#repo-url').val('https://github.com/' + repos[idx]);
                $.fn.zato.envRepo.handleConnect();
                return;
            }
        }

        // The App was not given the new repository, so its address is typed, or pasted, here.
        $('#repo-url').focus();

    }, function() {
        $('#repo-url').focus();
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.fillRepoList = function(repos) {

    const list = $('#repo-list');
    list.empty();

    repos.forEach(function(fullName) {
        list.append($('<option></option>').attr('value', 'https://github.com/' + fullName));
    });

    $.fn.zato.envRepo.state.knownRepos = repos;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.updateHint = function() {

    const hint = $.fn.zato.envRepo.state.hint;

    if(!hint) {
        return;
    }

    // The hint is for someone with no repository, and once the link in it was clicked there is one on the way.
    if($('#repo-url').val().trim() || $.fn.zato.envRepo.isCreating(false)) {
        hint.hide();
    }
    else {
        hint.show();
    }
};
