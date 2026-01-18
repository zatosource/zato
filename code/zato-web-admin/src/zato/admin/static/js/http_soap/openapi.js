
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.original_yaml = "";

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.init = function() {

    $.fn.zato.http_soap.openapi.original_yaml = $("#openapi-copy-paste-textarea").val();

    let openapi_import_content = `
        <input type="button" id="openapi-from-copy-paste" value="From copy/paste" onclick="$.fn.zato.http_soap.openapi.on_from_copy_paste();"/>
        <input type="button" id="openapi-from-url" value="From URL" onclick="$.fn.zato.http_soap.openapi.on_from_url();"/>
    `;

    tippy("#openapi-import-link", {
        content: openapi_import_content,
        allowHTML: true,
        theme: "light",
        trigger: "click",
        placement: "bottom",
        arrow: true,
        interactive: true,
    });

    $("#openapi-copy-paste-close").click($.fn.zato.http_soap.openapi.close_copy_paste_overlay);
    $("#openapi-copy-paste-cancel").click($.fn.zato.http_soap.openapi.close_copy_paste_overlay);
    $("#openapi-copy-paste-ok").click($.fn.zato.http_soap.openapi.on_copy_paste_ok);
    $("#openapi-table-import").click($.fn.zato.http_soap.openapi.on_table_import);
    $(".openapi-overlay-backdrop").click($.fn.zato.http_soap.openapi.close_copy_paste_overlay);

    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            if (!$("#openapi-copy-paste-overlay").hasClass("hidden")) {
                e.preventDefault();
                $.fn.zato.http_soap.openapi.close_copy_paste_overlay();
            }
        }
    });

    $.fn.zato.http_soap.openapi.init_draggable();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.init_draggable = function() {
    let overlay_content = document.querySelector("#openapi-copy-paste-overlay .openapi-overlay-content");
    let header = document.querySelector("#openapi-copy-paste-overlay .openapi-overlay-header");

    if (!overlay_content || !header) {
        return;
    }

    let is_dragging = false;
    let offset_x = 0;
    let offset_y = 0;

    header.addEventListener("mousedown", function(e) {
        if (e.target.classList.contains("openapi-close-button")) {
            return;
        }
        is_dragging = true;
        offset_x = e.clientX - overlay_content.offsetLeft;
        offset_y = e.clientY - overlay_content.offsetTop;
        overlay_content.style.position = "absolute";
        overlay_content.style.margin = "0";
    });

    document.addEventListener("mousemove", function(e) {
        if (!is_dragging) {
            return;
        }
        let new_x = e.clientX - offset_x;
        let new_y = e.clientY - offset_y;
        overlay_content.style.left = new_x + "px";
        overlay_content.style.top = new_y + "px";
    });

    document.addEventListener("mouseup", function() {
        is_dragging = false;
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_from_copy_paste = function() {
    $("#openapi-copy-paste-overlay").removeClass("hidden");
    $("#openapi-copy-paste-textarea").focus();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_from_url = function() {
    alert("From URL clicked");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.close_copy_paste_overlay = function() {
    $("#openapi-copy-paste-overlay").addClass("hidden");
    $("#openapi-copy-paste-textarea").val($.fn.zato.http_soap.openapi.original_yaml);
    $("#openapi-copy-paste-textarea").show();
    $("#openapi-data-table-container").hide().empty();
    $("#openapi-copy-paste-ok").show();
    $("#openapi-table-import").hide();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.show_table = function(data) {

    let rows = [];
    let servers = data.servers || [];
    let server = servers.length > 0 ? servers[0] : "";

    for (let i = 0; i < data.paths.length; i++) {
        let path_item = data.paths[i];
        rows.push({
            name: path_item.name,
            path: path_item.path,
            server: server,
            auth: path_item.auth,
            content_type: path_item.content_type
        });
    }

    let config = {
        container_id: "openapi-data-table-container",
        columns: [
            {label: "Name", field: "name"},
            {label: "URL path", field: "path"}
        ],
        rows: rows,
        hidden_fields: ["server", "auth", "content_type", "name", "path"],
        filter_placeholder: "Filter ..."
    };

    $("#openapi-copy-paste-textarea").hide();
    $("#openapi-data-table-container").css("display", "flex").css("flex-direction", "column");
    $("#openapi-copy-paste-ok").hide();
    $("#openapi-table-import").show();

    $.fn.zato.data_table_widget.render(config);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_table_import = function() {
    let selected = $.fn.zato.data_table_widget.get_selected("openapi-data-table-container", ["server", "auth", "content_type", "name", "path"]);

    if (selected.length === 0) {
        return;
    }

    let spinner_html = '<div id="openapi-import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 10001;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Creating ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $("body").append(spinner_html);

    $.ajax({
        type: "POST",
        url: "/zato/http-soap/openapi/import/",
        data: JSON.stringify(selected),
        contentType: "application/json",
        headers: {"X-CSRFToken": $.cookie("csrftoken")},
        success: function(response) {
            $("#openapi-import-spinner").remove();
            if (response.success) {
                $.fn.zato.http_soap.openapi.close_copy_paste_overlay();
            }
        },
        error: function(xhr) {
            $("#openapi-import-spinner").remove();
            let error_msg = "Import failed";
            try {
                let response = JSON.parse(xhr.responseText);
                if (response.error) {
                    error_msg = response.error;
                }
            } catch (e) {
                error_msg = xhr.responseText || error_msg;
            }
            console.error(error_msg);
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_copy_paste_ok = function() {
    let content = $("#openapi-copy-paste-textarea").val();

    let spinner_html = '<div id="openapi-import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 10001;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Importing ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $("body").append(spinner_html);

    $.ajax({
        type: "POST",
        url: "/zato/http-soap/openapi/parse/",
        data: content,
        contentType: "text/plain",
        headers: {"X-CSRFToken": $.cookie("csrftoken")},
        success: function(response) {
            $("#openapi-import-spinner").remove();
            if (response.success) {
                let parsed_data = JSON.parse(response.result);
                $.fn.zato.http_soap.openapi.show_table(parsed_data);
            } else {
                $("#openapi-copy-paste-textarea").val(response.error);
            }
        },
        error: function(xhr) {
            $("#openapi-import-spinner").remove();
            let error_msg = "Request failed";
            try {
                let response = JSON.parse(xhr.responseText);
                if (response.error) {
                    error_msg = response.error;
                }
            } catch (e) {
                error_msg = xhr.responseText || error_msg;
            }
            $("#openapi-copy-paste-textarea").val(error_msg);
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
