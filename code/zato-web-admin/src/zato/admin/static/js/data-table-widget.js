
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table_widget.render = function(config) {

    let container_id = config.container_id;
    let columns = config.columns;
    let rows = config.rows;
    let hidden_fields = config.hidden_fields || [];
    let filter_placeholder = config.filter_placeholder || "Filter ...";

    let html = '<div class="zato-data-table-widget">';

    html += '<div class="zato-data-table-filter">';
    html += '<input type="text" id="' + container_id + '-filter" placeholder="' + filter_placeholder + '" spellcheck="false" />';
    html += '</div>';

    html += '<div class="zato-data-table-container">';
    html += '<table class="zato-data-table" id="' + container_id + '-table">';

    html += '<thead><tr>';
    html += '<th><input type="checkbox" id="' + container_id + '-select-all" /></th>';
    for (let i = 0; i < columns.length; i++) {
        html += '<th>' + columns[i].label + '</th>';
    }
    html += '</tr></thead>';

    html += '<tbody>';
    for (let row_idx = 0; row_idx < rows.length; row_idx++) {
        let row = rows[row_idx];
        html += '<tr data-row-idx="' + row_idx + '">';
        html += '<td><input type="checkbox" class="' + container_id + '-row-checkbox" data-row-idx="' + row_idx + '" /></td>';

        for (let col_idx = 0; col_idx < columns.length; col_idx++) {
            let col = columns[col_idx];
            let value = row[col.field] || '';
            html += '<td title="' + $.fn.zato.data_table_widget.escape_html(value) + '">' + $.fn.zato.data_table_widget.escape_html(value) + '</td>';
        }

        for (let h = 0; h < hidden_fields.length; h++) {
            let hf = hidden_fields[h];
            let hf_value = row[hf] || '';
            html += '<input type="hidden" class="' + container_id + '-hidden-' + hf + '" data-row-idx="' + row_idx + '" value="' + $.fn.zato.data_table_widget.escape_html(hf_value) + '" />';
        }

        html += '</tr>';
    }
    html += '</tbody>';

    html += '</table>';
    html += '</div>';
    html += '</div>';

    $("#" + container_id).html(html);

    $.fn.zato.data_table_widget.bind_events(container_id, columns);
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table_widget.escape_html = function(text) {
    if (text === null || text === undefined) {
        return '';
    }
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table_widget.bind_events = function(container_id, columns) {

    $("#" + container_id + "-select-all").on("change", function() {
        let is_checked = $(this).is(":checked");
        $("." + container_id + "-row-checkbox:visible").prop("checked", is_checked);
        $("." + container_id + "-row-checkbox:visible").closest("tr").toggleClass("selected", is_checked);
    });

    $(document).on("change", "." + container_id + "-row-checkbox", function() {
        let is_checked = $(this).is(":checked");
        $(this).closest("tr").toggleClass("selected", is_checked);

        let all_checked = $("." + container_id + "-row-checkbox:visible").length === $("." + container_id + "-row-checkbox:visible:checked").length;
        $("#" + container_id + "-select-all").prop("checked", all_checked);
    });

    $("#" + container_id + "-filter").on("input", function() {
        let filter_value = $(this).val().toLowerCase();
        $("#" + container_id + "-table tbody tr").each(function() {
            let row_text = $(this).text().toLowerCase();
            if (row_text.indexOf(filter_value) > -1) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });

        let visible_rows = $("#" + container_id + "-table tbody tr:visible");
        let all_checked = visible_rows.length > 0 && visible_rows.find("." + container_id + "-row-checkbox").length === visible_rows.find("." + container_id + "-row-checkbox:checked").length;
        $("#" + container_id + "-select-all").prop("checked", all_checked);
    });
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table_widget.get_selected = function(container_id, hidden_fields) {
    let selected = [];
    $("." + container_id + "-row-checkbox:checked").each(function() {
        let row_idx = $(this).data("row-idx");
        let row_data = {};

        let tr = $(this).closest("tr");
        let cells = tr.find("td");

        for (let h = 0; h < hidden_fields.length; h++) {
            let hf = hidden_fields[h];
            row_data[hf] = $("." + container_id + "-hidden-" + hf + "[data-row-idx='" + row_idx + "']").val();
        }

        selected.push(row_data);
    });
    return selected;
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
