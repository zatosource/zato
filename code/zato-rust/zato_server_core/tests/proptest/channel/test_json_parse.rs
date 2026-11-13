use proptest::prelude::*;
use zato_server_core::channel::json_parse::{JsonBuilder, MAX_DEPTH, ParseError, parse};
use zato_server_core::channel::json_text::{push_json_float, push_json_string};

#[derive(Debug, Clone, PartialEq)]
enum Value {
    Null,
    Bool(bool),
    Integer(String),
    Float(f64),
    Text(String),
    Surrogates(Vec<u32>),
    Array(Vec<Self>),
    Object(Vec<(Self, Self)>),
}

struct Builder;

impl JsonBuilder for Builder {
    type Value = Value;
    type Error = ();

    fn null(&mut self) -> Result<Value, ()> {
        Ok(Value::Null)
    }

    fn boolean(&mut self, value: bool) -> Result<Value, ()> {
        Ok(Value::Bool(value))
    }

    fn integer(&mut self, literal: &str) -> Result<Value, ()> {
        Ok(Value::Integer(literal.to_owned()))
    }

    fn float(&mut self, literal: &str) -> Result<Value, ()> {
        literal.parse().map(Value::Float).map_err(drop)
    }

    fn string(&mut self, text: &str) -> Result<Value, ()> {
        Ok(Value::Text(text.to_owned()))
    }

    fn string_with_surrogates(&mut self, code_points: &[u32]) -> Result<Value, ()> {
        Ok(Value::Surrogates(code_points.to_vec()))
    }

    fn array(&mut self, items: Vec<Value>) -> Result<Value, ()> {
        Ok(Value::Array(items))
    }

    fn object(&mut self, members: Vec<(Value, Value)>) -> Result<Value, ()> {
        Ok(Value::Object(members))
    }
}

fn parsed(text: &str) -> Result<Value, ParseError<()>> {
    parse(text, &mut Builder)
}

fn text(value: &str) -> Value {
    Value::Text(value.to_owned())
}

fn write(value: &Value, out: &mut String) {
    match value {
        Value::Null | Value::Surrogates(_) => out.push_str("null"),
        Value::Bool(flag) => out.push_str(if *flag { "true" } else { "false" }),
        Value::Integer(literal) => out.push_str(literal),
        Value::Float(number) => push_json_float(out, *number),
        Value::Text(content) => push_json_string(out, content),
        Value::Array(items) => {
            out.push('[');
            for (position, item) in items.iter().enumerate() {
                if position > 0 {
                    out.push_str(", ");
                }
                write(item, out);
            }
            out.push(']');
        }
        Value::Object(members) => {
            out.push('{');
            for (position, (key, member)) in members.iter().enumerate() {
                if position > 0 {
                    out.push(',');
                }
                write(key, out);
                out.push_str(" :\n");
                write(member, out);
            }
            out.push('}');
        }
    }
}

#[test]
fn scalars_are_parsed() {
    assert_eq!(parsed(" null "), Ok(Value::Null));
    assert_eq!(parsed("true"), Ok(Value::Bool(true)));
    assert_eq!(parsed("-0"), Ok(Value::Integer("-0".to_owned())));
    assert_eq!(parsed("1.5e3"), Ok(Value::Float(1500.0)));
    assert_eq!(parsed("1E400"), Ok(Value::Float(f64::INFINITY)));
    assert_eq!(parsed("-Infinity"), Ok(Value::Float(f64::NEG_INFINITY)));
    assert!(matches!(parsed("NaN"), Ok(Value::Float(number)) if number.is_nan()));
}

#[test]
fn invalid_numbers_are_rejected() {
    assert!(parsed("01").is_err());
    assert!(parsed("1.").is_err());
    assert!(parsed(".5").is_err());
    assert!(parsed("1e").is_err());
    assert!(parsed("1e+").is_err());
    assert!(parsed("-").is_err());
    assert!(parsed("+1").is_err());
    assert!(parsed("-infinity").is_err());
    assert!(parsed("\u{661}").is_err());
}

#[test]
fn strings_are_decoded() {
    assert_eq!(parsed(r#""a\"b\\c\/d\b\f\n\r\t""#), Ok(text("a\"b\\c/d\u{8}\u{c}\n\r\t")));
    assert_eq!(parsed(r#""\u017c\u00e9""#), Ok(text("\u{17c}\u{e9}")));
    assert_eq!(parsed(r#""\ud83d\ude00""#), Ok(text("\u{1f600}")));
    assert_eq!(parsed("\"\u{7f}\""), Ok(text("\u{7f}")));
}

#[test]
fn surrogates_without_a_partner_are_kept() {
    assert_eq!(parsed(r#""a\ud83d""#), Ok(Value::Surrogates(vec![0x61, 0xD83D])));
    assert_eq!(parsed(r#""\ude00\ud83d""#), Ok(Value::Surrogates(vec![0xDE00, 0xD83D])));
    assert_eq!(parsed(r#""\ud83d\u0041""#), Ok(Value::Surrogates(vec![0xD83D, 0x41])));
}

#[test]
fn invalid_strings_are_rejected() {
    assert!(parsed("\"a\nb\"").is_err());
    assert!(parsed(r#""\x""#).is_err());
    assert!(parsed(r#""\u12""#).is_err());
    assert!(parsed(r#""\ud83d\uzzzz""#).is_err());
    assert!(parsed("\"abc").is_err());
}

#[test]
#[expect(clippy::literal_string_with_formatting_args, reason = "the JSON documents contain braces")]
fn containers_follow_the_grammar() {
    assert_eq!(parsed("[ ]"), Ok(Value::Array(vec![])));
    assert_eq!(parsed("{ }"), Ok(Value::Object(vec![])));
    assert!(parsed("[1,]").is_err());
    assert!(parsed("{\"a\":1,}").is_err());
    assert!(parsed("{\"a\" 1}").is_err());
    assert!(parsed("{1:1}").is_err());
    assert!(parsed("[1 2]").is_err());
    assert!(parsed("[1] x").is_err());
    assert!(parsed("").is_err());
    assert!(parsed(" \u{a0}1").is_err());
}

#[test]
fn deep_documents_are_left_to_python() {
    let deep = format!("{}{}", "[".repeat(MAX_DEPTH + 1), "]".repeat(MAX_DEPTH + 1));
    assert_eq!(parsed(&deep), Err(ParseError::TooDeep));

    let allowed = format!("{}{}", "[".repeat(MAX_DEPTH), "]".repeat(MAX_DEPTH));
    assert!(parsed(&allowed).is_ok());
}

fn value_strategy() -> impl Strategy<Value = Value> {
    let leaf = prop_oneof![
        Just(Value::Null),
        any::<bool>().prop_map(Value::Bool),
        any::<i64>().prop_map(|number| Value::Integer(number.to_string())),
        any::<f64>()
            .prop_filter("finite", |number| number.is_finite())
            .prop_map(Value::Float),
        "\\PC{0,12}".prop_map(Value::Text),
    ];

    leaf.prop_recursive(4, 32, 6, |inner| {
        prop_oneof![
            prop::collection::vec(inner.clone(), 0..6).prop_map(Value::Array),
            prop::collection::vec(("\\PC{0,8}".prop_map(Value::Text), inner), 0..6).prop_map(Value::Object),
        ]
    })
}

proptest! {

    #[test]
    fn written_documents_parse_back(value in value_strategy()) {
        let mut document = String::new();
        write(&value, &mut document);
        prop_assert_eq!(parsed(&document), Ok(value));
    }
}
