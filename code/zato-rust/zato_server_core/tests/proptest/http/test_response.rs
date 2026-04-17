use proptest::prelude::*;
use zato_server_core::http::response::parse_status_code;

proptest! {

    #[test]
    fn parse_status_code_valid(code in 100u16..600) {
        let s = format!("{} Whatever", code);
        let result = parse_status_code(&s);
        prop_assert_eq!(result.as_u16(), code);
    }

    #[test]
    fn parse_status_code_garbage_returns_200(s in "[^0-9]{1,20}") {
        let result = parse_status_code(&s);
        prop_assert_eq!(result.as_u16(), 200);
    }

    #[test]
    fn parse_status_code_bare_code(code in 100u16..600) {
        let s = code.to_string();
        let result = parse_status_code(&s);
        prop_assert_eq!(result.as_u16(), code);
    }

    #[test]
    fn parse_status_code_empty(_dummy in Just(())) {
        let result = parse_status_code("");
        prop_assert_eq!(result.as_u16(), 200);
    }
}
