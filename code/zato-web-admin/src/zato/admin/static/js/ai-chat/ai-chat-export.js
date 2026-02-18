var AIChatExport = {

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
        wrapper.className = 'ai-chat-export-trigger';
        wrapper.innerHTML = AIChatIcons.get('checklist', 25);

        var tooltip = document.createElement('div');
        tooltip.className = 'ai-chat-export-tooltip';
        tooltip.innerHTML = this.buildTooltipHtml();

        wrapper.appendChild(tooltip);
        this.container.appendChild(wrapper);
        this.tooltip = tooltip;
    },

    buildTooltipHtml: function() {
        var html = '<table>';
        for (var i = 0; i < this.groups.length; i++) {
            var group = this.groups[i];
            html += '<tr class="ai-chat-export-group-row"><td colspan="2">' + group.label + '</td></tr>';
            for (var j = 0; j < group.items.length; j++) {
                var item = group.items[j];
                html += '<tr class="ai-chat-export-item-row" data-export-id="' + item.id + '">';
                html += '<td>' + item.label + '</td>';
                html += '</tr>';
            }
        }
        html += '</table>';
        return html;
    },

    attachEvents: function() {
        var self = this;
        this.tooltip.addEventListener('click', function(e) {
            var row = e.target.closest('.ai-chat-export-item-row');
            if (row) {
                var exportId = row.getAttribute('data-export-id');
                self.handleExport(exportId);
            }
        });
    },

    handleExport: function(exportId) {
        var label = this.getExportLabel(exportId);
        alert('Export: ' + label);
    },

    getExportLabel: function(exportId) {
        for (var i = 0; i < this.groups.length; i++) {
            var group = this.groups[i];
            for (var j = 0; j < group.items.length; j++) {
                if (group.items[j].id === exportId) {
                    return group.items[j].label;
                }
            }
        }
        return exportId;
    }

};
