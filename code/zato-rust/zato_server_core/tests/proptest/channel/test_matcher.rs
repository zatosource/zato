use proptest::prelude::*;
use zato_server_core::channel::matcher::{ChannelPattern, ChannelSpec, PatternError, escape_url_path, get_match_target, python_re_escape};

fn methods_allowed() -> Vec<String> {
    vec!["GET".to_owned(), "POST".to_owned(), "DELETE".to_owned()]
}

#[expect(clippy::unwrap_used, reason = "a pattern that does not compile fails the test")]
fn compile(method: &str, url_path: &str, match_slash: bool) -> ChannelPattern {
    let spec = ChannelSpec {
        method,
        http_accept: None,
        url_path,
        match_slash,
    };
    let target = get_match_target(&spec, &methods_allowed());
    ChannelPattern::compile(&spec, &methods_allowed(), &target).unwrap()
}

#[test]
fn python_escape_characters() {
    assert_eq!(python_re_escape("a.b-c d"), "a\\.b\\-c\\ d");
    assert_eq!(python_re_escape("/api/x_y:z"), "/api/x_y:z");
    assert_eq!(python_re_escape("&~#"), "\\&\\~\\#");
}

#[test]
fn url_path_parameters_stay_unescaped() {
    assert_eq!(escape_url_path("/api/customer.{id}/x"), "/api/customer\\.{id}/x");
    assert_eq!(escape_url_path("/api/{a"), "/api/\\{a");
    assert_eq!(escape_url_path("/api/a}{b}"), "/api/a\\}{b}");
}

#[test]
fn match_target_of_a_channel_without_method() {
    let spec = ChannelSpec {
        method: "",
        http_accept: None,
        url_path: "/api/customer",
        match_slash: true,
    };
    assert_eq!(
        get_match_target(&spec, &methods_allowed()),
        ":::(?:GET|POST|DELETE):::haanyHTTP_SEPhaany:::/api/customer"
    );
}

#[test]
fn static_path_matches_with_no_parameters() {
    let pattern = compile("GET", "/api/customer", true);
    assert_eq!(pattern.match_target(":::GET:::haanyHTTP_SEPhaany:::/api/customer"), Some(vec![]));
    assert_eq!(pattern.match_target(":::GET:::haanyHTTP_SEPhaany:::/api/customer\n"), Some(vec![]));
    assert_eq!(pattern.match_target(":::GET:::haanyHTTP_SEPhaany:::/api/customer/"), None);
    assert_eq!(pattern.match_target(":::POST:::haanyHTTP_SEPhaany:::/api/customer"), None);
}

#[test]
fn any_accept_matches_any_value_without_separator() {
    let pattern = compile("GET", "/api/customer", true);
    assert!(pattern.match_target(":::GET:::applicationHTTP_SEPjson:::/api/customer").is_some());
}

#[test]
fn parameters_are_returned_by_name() {
    let pattern = compile("", "/api/customer/{customer_id}/order/{order_id}", false);
    let parameters = pattern
        .match_target(":::POST:::haanyHTTP_SEPhaany:::/api/customer/123/order/John Smith")
        .unwrap();
    assert_eq!(
        parameters,
        vec![
            ("customer_id".to_owned(), "123".to_owned()),
            ("order_id".to_owned(), "John Smith".to_owned())
        ]
    );
}

#[test]
fn match_slash_decides_whether_parameters_span_segments() {
    let target = ":::GET:::haanyHTTP_SEPhaany:::/api/file/a/b";
    assert!(compile("GET", "/api/file/{name}", true).match_target(target).is_some());
    assert!(compile("GET", "/api/file/{name}", false).match_target(target).is_none());
}

#[test]
fn internal_channels_are_recognized() {
    assert!(compile("GET", "/zato/ping", true).is_internal());
    assert!(!compile("GET", "/api/zato/ping", true).is_internal());
}

#[test]
fn unsupported_definitions_are_reported() {
    let spec = ChannelSpec {
        method: "GET",
        http_accept: None,
        url_path: "/api/{id}/{id}",
        match_slash: true,
    };
    let target = get_match_target(&spec, &methods_allowed());
    assert!(matches!(
        ChannelPattern::compile(&spec, &methods_allowed(), &target),
        Err(PatternError::UnsupportedPath)
    ));

    let spec = ChannelSpec {
        method: "GET",
        http_accept: None,
        url_path: "/api/{a.b}",
        match_slash: true,
    };
    let target = get_match_target(&spec, &methods_allowed());
    assert!(matches!(
        ChannelPattern::compile(&spec, &methods_allowed(), &target),
        Err(PatternError::UnsupportedPath)
    ));

    let spec = ChannelSpec {
        method: "GET",
        http_accept: None,
        url_path: "/api",
        match_slash: true,
    };
    assert!(matches!(
        ChannelPattern::compile(&spec, &methods_allowed(), ":::GET:::x:::/api"),
        Err(PatternError::TargetMismatch)
    ));

    let spec = ChannelSpec {
        method: "G.T",
        http_accept: None,
        url_path: "/api",
        match_slash: true,
    };
    let target = get_match_target(&spec, &methods_allowed());
    assert!(matches!(
        ChannelPattern::compile(&spec, &methods_allowed(), &target),
        Err(PatternError::UnsupportedMethod)
    ));
}

proptest! {

    #[test]
    fn literal_paths_match_only_themselves(path in "/[a-zA-Z0-9.+*?()|-]{1,20}", other in "/[a-zA-Z0-9.+*?()|-]{1,20}") {
        let pattern = compile("GET", &path, true);
        let own = format!(":::GET:::haanyHTTP_SEPhaany:::{path}");
        let different = format!(":::GET:::haanyHTTP_SEPhaany:::{other}");
        prop_assert!(pattern.match_target(&own).is_some());
        prop_assert_eq!(pattern.match_target(&different).is_some(), path == other);
    }

    #[test]
    fn parameter_values_are_captured(value in "[a-zA-Z0-9 $.:|=~^%@+,;!()-]{1,20}") {
        let pattern = compile("GET", "/api/customer/{customer_id}", false);
        let target = format!(":::GET:::haanyHTTP_SEPhaany:::/api/customer/{value}");
        let parameters = pattern.match_target(&target).unwrap();
        prop_assert_eq!(parameters, vec![("customer_id".to_owned(), value)]);
    }
}
