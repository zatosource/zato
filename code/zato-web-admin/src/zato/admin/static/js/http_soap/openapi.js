
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.original_yaml = "";

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.highlight_yaml = function(text) {
    let escaped = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    let highlighted = escaped
        .replace(/(#.*)$/gm, '<span class="hl-comment">$1</span>')
        .replace(/^(\s*)([a-zA-Z_][a-zA-Z0-9_-]*)(:)/gm, '$1<span class="hl-key">$2</span>$3')
        .replace(/:\s*("(?:[^"\\]|\\.)*")/g, ': <span class="hl-str">$1</span>')
        .replace(/:\s*('(?:[^'\\]|\\.)*')/g, ": <span class=\"hl-str\">$1</span>")
        .replace(/:\s*(true|false|null)\b/gi, ': <span class="hl-bool">$1</span>')
        .replace(/:\s*(-?\d+\.?\d*)\b/g, ': <span class="hl-num">$1</span>');

    return highlighted;
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.sync_highlight = function() {
    let text = $("#openapi-copy-paste-textarea").val();
    let highlighted = $.fn.zato.http_soap.openapi.highlight_yaml(text);
    $("#openapi-highlight-layer").html(highlighted + "\n");

    let textarea = document.getElementById("openapi-copy-paste-textarea");
    let layer = document.getElementById("openapi-highlight-layer");
    layer.scrollTop = textarea.scrollTop;
    layer.scrollLeft = textarea.scrollLeft;
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.init = function() {

    $.fn.zato.http_soap.openapi.original_yaml = $("#openapi-copy-paste-textarea").val();

    $.fn.zato.http_soap.openapi.sync_highlight();
    $("#openapi-copy-paste-textarea").on("input", $.fn.zato.http_soap.openapi.sync_highlight);
    $("#openapi-copy-paste-textarea").on("scroll", function() {
        let layer = document.getElementById("openapi-highlight-layer");
        layer.scrollTop = this.scrollTop;
        layer.scrollLeft = this.scrollLeft;
    });

    let url_params = new URLSearchParams(window.location.search);
    if (url_params.get("openapi_imported") === "1") {
        let url = new URL(window.location.href);
        url.searchParams.delete("openapi_imported");
        window.history.replaceState({}, document.title, url.toString());

        if (!document.getElementById("openapi-flash-style")) {
            let style = document.createElement("style");
            style.id = "openapi-flash-style";
            style.textContent = "@keyframes flash-green { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }";
            document.head.appendChild(style);
        }

        $("#user-message").text("OK, imported").addClass("user-message-success");
        $("#user-message-div").show();
        $("#user-message").css("animation", "flash-green 0.8s ease-in-out 2");
    }

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
    $("#openapi-url-ok").click($.fn.zato.http_soap.openapi.on_url_ok);
    $("#openapi-back").click($.fn.zato.http_soap.openapi.on_back);
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
    $("#openapi-copy-paste-overlay").removeClass("hidden");
    $("#openapi-editor-container").hide();
    $("#openapi-copy-paste-ok").hide();
    $("#openapi-url-input-container").css("display", "flex");
    $("#openapi-url-ok").show();
    $("#openapi-url-input").val("").focus();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.close_copy_paste_overlay = function() {
    $("#openapi-copy-paste-overlay").addClass("hidden");
    $("#openapi-copy-paste-textarea").val($.fn.zato.http_soap.openapi.original_yaml);
    $.fn.zato.http_soap.openapi.sync_highlight();
    $("#openapi-copy-paste-textarea").show();
    $("#openapi-editor-container").show();
    $("#openapi-url-input-container").hide();
    $("#openapi-url-input").val("");
    $("#openapi-data-table-container").hide().empty();
    $("#openapi-copy-paste-ok").show();
    $("#openapi-url-ok").hide();
    $("#openapi-back").hide();
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
            auth_server_url: path_item.auth_server_url,
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
        hidden_fields: ["server", "auth", "auth_server_url", "content_type", "name", "path"],
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
    let selected = $.fn.zato.data_table_widget.get_selected("openapi-data-table-container", ["server", "auth", "auth_server_url", "content_type", "name", "path"]);

    if (selected.length === 0) {
        return;
    }

    $.fn.zato.http_soap.openapi.show_spinner("Importing ...");

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
                let url = new URL(window.location.href);
                url.searchParams.set("openapi_imported", "1");
                window.location.href = url.toString();
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

    $.fn.zato.http_soap.openapi.show_spinner("Reading ...");

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

$.fn.zato.http_soap.openapi.show_spinner = function(message) {
    let spinner_html = '<div id="openapi-import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 10001;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>' + message + '</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $("body").append(spinner_html);
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_url_ok = function() {
    let url = $("#openapi-url-input").val().trim();

    if (!url) {
        return;
    }

    $.fn.zato.http_soap.openapi.show_spinner("Fetching ...");

    $.ajax({
        type: "POST",
        url: "/zato/http-soap/openapi/fetch/",
        data: JSON.stringify({url: url}),
        contentType: "application/json",
        headers: {"X-CSRFToken": $.cookie("csrftoken")},
        success: function(response) {
            $("#openapi-import-spinner").remove();

            if (!response.success) {
                $("#openapi-copy-paste-textarea").val(response.error).show();
                $("#openapi-url-input-container").hide();
                $("#openapi-url-ok").hide();
                $("#openapi-copy-paste-ok").hide();
                $("#openapi-back").show();
                return;
            }

            let content = response.content;

            $("#openapi-url-input-container").hide();
            $("#openapi-url-ok").hide();

            $.fn.zato.http_soap.openapi.show_spinner("Reading ...");

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
                        $("#openapi-copy-paste-textarea").val(response.error).show();
                        $("#openapi-copy-paste-ok").hide();
                        $("#openapi-back").show();
                    }
                },
                error: function(xhr) {
                    $("#openapi-import-spinner").remove();
                    let error_msg = "Parse failed";
                    try {
                        let resp = JSON.parse(xhr.responseText);
                        if (resp.error) {
                            error_msg = resp.error;
                        }
                    } catch (e) {
                        error_msg = xhr.responseText || error_msg;
                    }
                    $("#openapi-copy-paste-textarea").val(error_msg).show();
                    $("#openapi-copy-paste-ok").hide();
                    $("#openapi-back").show();
                }
            });
        },
        error: function(xhr) {
            $("#openapi-import-spinner").remove();
            let error_msg = "Failed to fetch URL";
            try {
                let resp = JSON.parse(xhr.responseText);
                if (resp.error) {
                    error_msg = resp.error;
                }
            } catch (e) {
                error_msg = xhr.responseText || error_msg;
            }
            $("#openapi-copy-paste-textarea").val(error_msg).show();
            $("#openapi-url-input-container").hide();
            $("#openapi-url-ok").hide();
            $("#openapi-copy-paste-ok").hide();
            $("#openapi-back").show();
        }
    });
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_back = function() {
    $("#openapi-copy-paste-textarea").hide();
    $("#openapi-copy-paste-ok").hide();
    $("#openapi-back").hide();
    $("#openapi-url-input-container").css("display", "flex");
    $("#openapi-url-ok").show();
    $("#openapi-url-input").focus();
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
