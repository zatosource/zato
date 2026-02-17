(function() {
    'use strict';

    var AIChatDiff = {

        computeDiff: function(oldContent, newContent) {
            var oldLines = oldContent ? oldContent.split('\n') : [];
            var newLines = newContent ? newContent.split('\n') : [];

            var result = [];
            var oldIdx = 0;
            var newIdx = 0;

            var lcs = this.computeLCS(oldLines, newLines);
            var lcsIdx = 0;

            while (oldIdx < oldLines.length || newIdx < newLines.length) {
                if (lcsIdx < lcs.length && oldIdx < oldLines.length && newIdx < newLines.length &&
                    oldLines[oldIdx] === lcs[lcsIdx] && newLines[newIdx] === lcs[lcsIdx]) {
                    result.push({type: 'unchanged', line: oldLines[oldIdx]});
                    oldIdx++;
                    newIdx++;
                    lcsIdx++;
                } else if (newIdx < newLines.length && (lcsIdx >= lcs.length || newLines[newIdx] !== lcs[lcsIdx])) {
                    result.push({type: 'added', line: newLines[newIdx]});
                    newIdx++;
                } else if (oldIdx < oldLines.length && (lcsIdx >= lcs.length || oldLines[oldIdx] !== lcs[lcsIdx])) {
                    result.push({type: 'removed', line: oldLines[oldIdx]});
                    oldIdx++;
                } else {
                    break;
                }
            }

            return result;
        },

        computeLCS: function(a, b) {
            var m = a.length;
            var n = b.length;
            var dp = [];

            for (var i = 0; i <= m; i++) {
                dp[i] = [];
                for (var j = 0; j <= n; j++) {
                    if (i === 0 || j === 0) {
                        dp[i][j] = 0;
                    } else if (a[i - 1] === b[j - 1]) {
                        dp[i][j] = dp[i - 1][j - 1] + 1;
                    } else {
                        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                    }
                }
            }

            var lcs = [];
            var i = m;
            var j = n;
            while (i > 0 && j > 0) {
                if (a[i - 1] === b[j - 1]) {
                    lcs.unshift(a[i - 1]);
                    i--;
                    j--;
                } else if (dp[i - 1][j] > dp[i][j - 1]) {
                    i--;
                } else {
                    j--;
                }
            }

            return lcs;
        },

        renderDiff: function(oldContent, newContent, isNew) {
            var escapedNewContent = this.escapeHtml(newContent || '');
            
            if (isNew) {
                var lines = newContent ? newContent.split('\n') : [];
                var html = '<div class="ai-diff-container" data-new-content="' + escapedNewContent.replace(/"/g, '&quot;') + '">';
                html += '<div class="ai-diff-header ai-diff-new"><span>New file</span><button class="ai-diff-copy ai-diff-copy-file">Copy file</button></div>';
                html += '<div class="ai-diff-content">';
                for (var i = 0; i < lines.length; i++) {
                    html += '<div class="ai-diff-line ai-diff-added"><span class="ai-diff-sign">+</span><span class="ai-diff-text">' + this.escapeHtml(lines[i]) + '</span></div>';
                }
                html += '</div></div>';
                return html;
            }

            var diff = this.computeDiff(oldContent, newContent);
            var diffText = this.getDiffText(diff);
            var escapedDiffText = this.escapeHtml(diffText).replace(/"/g, '&quot;');

            var hunks = this.countHunks(diff);
            var hunkCount = hunks.length;
            var hunkLabel = hunkCount === 1 ? '1 edit' : hunkCount + ' edits';
            
            var html = '<div class="ai-diff-container" data-diff-content="' + escapedDiffText + '" data-hunk-count="' + hunkCount + '" data-current-hunk="0">';
            html += '<div class="ai-diff-header ai-diff-modified"><span>Modified · ' + hunkLabel;
            if (hunkCount > 1) {
                html += ' · <span class="ai-diff-nav"><button class="ai-diff-nav-btn ai-diff-nav-up" title="Previous change">▲</button><button class="ai-diff-nav-btn ai-diff-nav-down" title="Next change">▼</button></span>';
            }
            html += '</span><button class="ai-diff-copy ai-diff-copy-diff">Copy diff</button></div>';
            html += '<div class="ai-diff-content">';

            var currentHunk = -1;
            var inHunk = false;
            for (var i = 0; i < diff.length; i++) {
                var item = diff[i];
                var lineClass = 'ai-diff-line';
                var sign = ' ';
                var hunkAttr = '';

                if (item.type === 'added' || item.type === 'removed') {
                    if (!inHunk) {
                        currentHunk++;
                        inHunk = true;
                    }
                    hunkAttr = ' data-hunk="' + currentHunk + '"';
                    if (item.type === 'added') {
                        lineClass += ' ai-diff-added';
                        sign = '+';
                    } else {
                        lineClass += ' ai-diff-removed';
                        sign = '-';
                    }
                } else {
                    inHunk = false;
                }

                html += '<div class="' + lineClass + '"' + hunkAttr + '><span class="ai-diff-sign">' + sign + '</span><span class="ai-diff-text">' + this.escapeHtml(item.line) + '</span></div>';
            }

            html += '</div></div>';
            return html;
        },

        getDiffText: function(diff) {
            var lines = [];
            for (var i = 0; i < diff.length; i++) {
                var item = diff[i];
                var sign = ' ';
                if (item.type === 'added') {
                    sign = '+';
                } else if (item.type === 'removed') {
                    sign = '-';
                }
                lines.push(sign + item.line);
            }
            return lines.join('\n');
        },

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        countHunks: function(diff) {
            var hunks = [];
            var inHunk = false;
            for (var i = 0; i < diff.length; i++) {
                var item = diff[i];
                if (item.type === 'added' || item.type === 'removed') {
                    if (!inHunk) {
                        hunks.push(i);
                        inHunk = true;
                    }
                } else {
                    inHunk = false;
                }
            }
            return hunks;
        },

        navigateToHunk: function(container, hunkIndex) {
            console.log('[NAV-HUNK] navigateToHunk called, hunkIndex:', hunkIndex);
            var hunkCount = parseInt(container.getAttribute('data-hunk-count') || '0', 10);
            console.log('[NAV-HUNK] hunkCount:', hunkCount);
            if (hunkCount === 0) {
                console.log('[NAV-HUNK] hunkCount is 0, returning');
                return;
            }

            if (hunkIndex < 0) hunkIndex = hunkCount - 1;
            if (hunkIndex >= hunkCount) hunkIndex = 0;

            container.setAttribute('data-current-hunk', hunkIndex);
            console.log('[NAV-HUNK] set data-current-hunk to:', hunkIndex);

            var diffContent = container.querySelector('.ai-diff-content');
            if (!diffContent) {
                console.log('[NAV-HUNK] no diffContent found');
                return;
            }

            var selector = '.ai-diff-line[data-hunk="' + hunkIndex + '"]';
            console.log('[NAV-HUNK] selector:', selector);
            var firstLineOfHunk = container.querySelector(selector);
            console.log('[NAV-HUNK] firstLineOfHunk:', firstLineOfHunk);
            if (firstLineOfHunk) {
                var allLines = container.querySelectorAll('.ai-diff-line');
                console.log('[NAV-HUNK] allLines count:', allLines.length);
                var lineIndex = Array.prototype.indexOf.call(allLines, firstLineOfHunk);
                console.log('[NAV-HUNK] lineIndex:', lineIndex);
                var scrollToIndex = Math.max(0, lineIndex - 4);
                console.log('[NAV-HUNK] scrollToIndex:', scrollToIndex);
                var scrollTarget = allLines[scrollToIndex];
                console.log('[NAV-HUNK] scrollTarget:', scrollTarget);
                if (scrollTarget) {
                    console.log('[NAV-HUNK] scrolling diffContent');
                    var targetTop = scrollTarget.offsetTop - diffContent.firstElementChild.offsetTop;
                    console.log('[NAV-HUNK] targetTop:', targetTop, 'scrollTarget.offsetTop:', scrollTarget.offsetTop, 'firstChild.offsetTop:', diffContent.firstElementChild.offsetTop);
                    diffContent.scrollTop = Math.max(0, targetTop);
                } else {
                    console.log('[NAV-HUNK] no scrollTarget');
                }
            } else {
                console.log('[NAV-HUNK] no firstLineOfHunk found');
            }
        }
    };

    window.AIChatDiff = AIChatDiff;

})();
