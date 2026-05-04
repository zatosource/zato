use zato_server_core::http::response::parse_status_code;

#[test]
fn status_200() {
    assert_eq!(parse_status_code("200 OK").as_u16(), 200);
}

#[test]
fn status_404() {
    assert_eq!(parse_status_code("404 Not Found").as_u16(), 404);
}

#[test]
fn status_500() {
    assert_eq!(parse_status_code("500 Internal Server Error").as_u16(), 500);
}

#[test]
fn status_empty_defaults_200() {
    assert_eq!(parse_status_code("").as_u16(), 200);
}

#[test]
fn status_garbage_defaults_200() {
    assert_eq!(parse_status_code("abc").as_u16(), 200);
}

#[test]
fn status_bare_code() {
    assert_eq!(parse_status_code("301").as_u16(), 301);
}

#[test]
fn status_100() {
    assert_eq!(parse_status_code("100 Continue").as_u16(), 100);
}

#[test]
fn status_599() {
    assert_eq!(parse_status_code("599 Custom").as_u16(), 599);
}
