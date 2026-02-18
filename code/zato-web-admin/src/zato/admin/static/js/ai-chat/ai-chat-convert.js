var AIChatConvert = {

    groups: [
        {
            id: 'documentation',
            label: 'Documentation',
            items: [
                { id: 'runbook', label: 'Runbook' },
                { id: 'faq', label: 'FAQ entry' },
                { id: 'training', label: 'Training material' },
                { id: 'onboarding', label: 'Onboarding checklist' }
            ]
        },
        {
            id: 'code',
            label: 'Code & scripts',
            items: [
                { id: 'shell-script', label: 'Shell script' },
                { id: 'test-cases', label: 'Test cases' },
                { id: 'api-test-suite', label: 'API test suite' },
                { id: 'migration-script', label: 'Migration script' }
            ]
        },
        {
            id: 'operations',
            label: 'Operations',
            items: [
                { id: 'monitoring-checklist', label: 'Monitoring checklist' },
                { id: 'alert-rules', label: 'Alert rules' },
                { id: 'rollback-procedure', label: 'Rollback procedure' },
                { id: 'config-template', label: 'Configuration template' }
            ]
        },
        {
            id: 'reports',
            label: 'Reports & records',
            items: [
                { id: 'incident-report', label: 'Incident report' },
                { id: 'decision-log', label: 'Decision log' },
                { id: 'changelog', label: 'Changelog entry' },
                { id: 'security-audit', label: 'Security audit notes' }
            ]
        },
        {
            id: 'diagrams',
            label: 'Diagrams & visuals',
            items: [
                { id: 'flowchart', label: 'Troubleshooting flowchart' },
                { id: 'dependency-map', label: 'Dependency map' }
            ]
        },
        {
            id: 'other',
            label: 'Other formats',
            items: [
                { id: 'code-review', label: 'Code review comments' },
                { id: 'performance-guide', label: 'Performance tuning guide' },
                { id: 'sla', label: 'SLA document' }
            ]
        }
    ],

    init: function(container) {
        this.container = container;
        this.render();
        this.attachEvents();
    },

    render: function() {
        var wrapper = document.createElement('span');
        wrapper.className = 'ai-chat-convert-trigger';
        wrapper.setAttribute('data-tooltip', 'Convert chat to ..');
        wrapper.innerHTML = AIChatIcons.get('checklist', 25);

        var tooltip = document.createElement('div');
        tooltip.className = 'ai-chat-convert-tooltip';
        tooltip.innerHTML = this.buildTooltipHtml();

        wrapper.appendChild(tooltip);
        this.container.appendChild(wrapper);
        this.tooltip = tooltip;
    },

    buildTooltipHtml: function() {
        var html = '<table>';
        for (var i = 0; i < this.groups.length; i++) {
            var group = this.groups[i];
            html += '<tr class="ai-chat-convert-group-row"><td colspan="2">' + group.label + '</td></tr>';
            for (var j = 0; j < group.items.length; j++) {
                var item = group.items[j];
                html += '<tr class="ai-chat-convert-item-row" data-convert-id="' + item.id + '">';
                html += '<td>' + item.label + '</td>';
                html += '</tr>';
            }
        }
        html += '</table>';
        return html;
    },

    attachEvents: function() {
        var self = this;
        var wrapper = this.container.querySelector('.ai-chat-convert-trigger');

        wrapper.addEventListener('click', function(e) {
            if (e.target.closest('.ai-chat-convert-tooltip')) {
                return;
            }
            e.stopPropagation();
            if (window.AIChatTooltip) {
                AIChatTooltip.hide();
            }
            self.toggle();
        });

        this.tooltip.addEventListener('click', function(e) {
            var row = e.target.closest('.ai-chat-convert-item-row');
            if (row) {
                var convertId = row.getAttribute('data-convert-id');
                self.handleConvert(convertId);
                self.close();
            }
        });

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.ai-chat-convert-trigger')) {
                self.close();
            }
        });
    },

    toggle: function() {
        if (this.tooltip.classList.contains('open')) {
            this.close();
        } else {
            this.open();
        }
    },

    open: function() {
        this.tooltip.classList.add('open');
    },

    close: function() {
        this.tooltip.classList.remove('open');
    },

    handleConvert: function(convertId) {
        var label = this.getConvertLabel(convertId);
        alert('Convert to: ' + label);
    },

    getConvertLabel: function(convertId) {
        for (var i = 0; i < this.groups.length; i++) {
            var group = this.groups[i];
            for (var j = 0; j < group.items.length; j++) {
                if (group.items[j].id === convertId) {
                    return group.items[j].label;
                }
            }
        }
        return convertId;
    }

};
