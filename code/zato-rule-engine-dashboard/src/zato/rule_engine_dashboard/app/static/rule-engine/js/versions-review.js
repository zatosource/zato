'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

versionsView.commentsHtml = function() {
    var self = this;
    var html = '';

    versionsModel.comments().forEach(function(comment) {
        var anchorText = 'on ' + comment.anchor.slice('rule-'.length);
        html += '<div class="versions-comment"><span class="versions-comment-anchor">' +
            shared.escape(anchorText) + '</span>' +
            '<span class="versions-comment-author">' + shared.escape(comment.author) + ', ' +
            self.whenText(comment.createdAt) + '</span>' +
            '<div class="versions-comment-text">' + shared.escape(comment.text) + '</div></div>';
    });

    var keys = versionsModel.reviewableKeys();
    if (keys.length === 0) {
        return html;
    }

    var options = keys.map(function(key) {
        var label = 'on ' + key.slice('rule-'.length);
        return '<option value="' + shared.escape(key) + '">' + shared.escape(label) + '</option>';
    }).join('');

    html += '<div class="versions-comment-form">' +
        '<select id="versions-comment-anchor" class="versions-select">' + options + '</select>' +
        '<input type="text" id="versions-comment-text" placeholder="A comment for the author...">' +
        '<button class="button-mini" onclick="versionsView.addComment(this)">Add</button></div>';

    return html;
};

// ////////////////////////////////////////////////////////////////////////

versionsView.renderReview = function() {
    var card = document.getElementById('versions-review-card');
    var approval = versionsModel.approval;

    if (approval === null) {
        card.innerHTML = '';
        return;
    }

    var html = '<div class="versions-review-card">';

    var gateText = approval.gate_enabled ? 'on' : 'off';
    html += '<div class="versions-review-row"><span>Approval gate</span><b>' + gateText +
        ' <button class="button-mini" onclick="versionsView.setGate(this, ' + !approval.gate_enabled + ')">' +
        (approval.gate_enabled ? 'Turn off' : 'Turn on') + '</button></b></div>';

    if (approval.gate_enabled) {
        var selfText = approval.allow_self_approval ? 'allowed' : 'not allowed';
        html += '<div class="versions-review-row"><span>Self-approval</span><b>' + selfText +
            ' <button class="button-mini" ' +
            'onclick="versionsView.setSelfApproval(this, ' + !approval.allow_self_approval + ')">' +
            (approval.allow_self_approval ? 'Forbid' : 'Allow') + '</button></b></div>';
    }

    if (approval.is_approved) {
        var row = approval.approval;
        html += '<div class="versions-review-row"><span>v' + approval.version + '</span><b>approved by ' +
            shared.escape(row.approver) + ', ' + this.whenText(row.created_at) + '</b></div>';

        if (row.comment !== null) {
            html += '<div class="versions-review-row"><span>Comment</span><b>' + shared.escape(row.comment) +
                '</b></div>';
        }

        var matchText = approval.content_matches ? 'matches the approval' : 'differs from what was approved';
        html += '<div class="versions-review-row"><span>Content</span><b>' + matchText + '</b></div>';
    } else {
        html += '<div class="versions-review-row"><span>v' + approval.version + '</span><b>not approved yet</b></div>';
        html += '<button class="button-primary versions-review-button" onclick="versionsView.approve(this)">' +
            'Approve v' + approval.version + '</button>';
    }

    if (versionsModel.toNumber === versionsModel.liveVersion) {
        html += '<div class="versions-note">Live.</div>';
    } else {
        html += '<button class="button-primary versions-review-button" onclick="versionsView.publish(this)">Publish v' +
            versionsModel.toNumber + '</button>';
    }

    html += '</div>';
    card.innerHTML = html;
};

// ////////////////////////////////////////////////////////////////////////

})();
