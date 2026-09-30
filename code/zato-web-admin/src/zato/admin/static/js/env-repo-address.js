// The address of the repository and the messages on its field - what the field accepts, how it reads,
// and what it says when it does not.

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.showStatus = function(message, isOK) {

    const config = $.fn.zato.envRepo.config;
    const status = $('#env-repo-status');

    status.removeClass('show fade status-message-success status-message-error');
    status.text(message).addClass('show ' + (isOK ? 'status-message-success' : 'status-message-error'));

    if(isOK) {
        setTimeout(function() {
            status.addClass('fade');
            setTimeout(function() {
                status.removeClass('show fade status-message-success');
            }, 500);
        }, config.statusFadeDelay);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.clearStatus = function() {
    $('#env-repo-status').removeClass('show fade status-message-success status-message-error').text('');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.showFieldError = function(message) {

    $('#repo-url').addClass('env-repo-error').focus();
    $.fn.zato.envRepo.showStatus(message, false);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.clearFieldError = function() {

    $('#repo-url').removeClass('env-repo-error');
    $.fn.zato.envRepo.clearStatus();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.envRepo.isAddressValid = function(address) {

    const patterns = $.fn.zato.envRepo.config.repoPatterns;

    for(let idx = 0; idx < patterns.length; idx++) {
        if(patterns[idx].test(address)) {
            return true;
        }
    }

    return false;
};

// ////////////////////////////////////////////////////////////////////////

// The owner and name out of any of the address forms the input accepts.
$.fn.zato.envRepo.parseAddress = function(address) {

    const path = address.replace(/^(?:https?:\/\/)?(?:www\.)?github\.com\//, '').replace(/^(?:ssh:\/\/)?git@github\.com[:/]/, '');
    const parts = path.split(/[/?#]/);

    const out = {
        owner: parts[0],
        name: parts[1].replace(/\.git$/, ''),
    };

    out.full_name = out.owner + '/' + out.name;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// GitHub's page for a new deploy key of the repository.
$.fn.zato.envRepo.getKeyUrl = function(repo) {

    const config = $.fn.zato.envRepo.config;

    const out = config.deployKeyUrl.replace('{owner}', repo.owner).replace('{name}', repo.name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The address is checked here first, nothing is sent until it has the right shape.
$.fn.zato.envRepo.getValidAddress = function() {

    const config = $.fn.zato.envRepo.config;
    const address = $('#repo-url').val().trim();

    $.fn.zato.envRepo.clearFieldError();

    if(!address) {
        $.fn.zato.envRepo.showFieldError(config.emptyAddressMessage);
        return null;
    }

    if(!$.fn.zato.envRepo.isAddressValid(address)) {
        $.fn.zato.envRepo.showFieldError(config.badAddressMessage);
        return null;
    }

    return address;
};
