//! Match targets of REST channels and the regular expressions they are compiled to.
//!
//! A match target has the form `:::METHOD:::ACCEPT:::PATH` and is built from a channel definition
//! exactly as `get_match_target` of `zato.common.util.url_dispatcher` builds it. Requests are turned
//! into a target of the same form and the first channel whose expression matches it handles the request.

use std::collections::HashSet;
use std::fmt;
use std::sync::OnceLock;

use regex::Regex;

use super::path::{ACCEPT_ANY_PAIR, to_internal_accept};

/// Separator of the parts of a match target.
pub const TARGET_SEPARATOR: &str = ":::";

/// Part of a match target that identifies a path of an internal Zato channel.
const INTERNAL_PATH_INDICATOR: &str = ":::/zato/";

/// Characters that `re.escape` of Python precedes with a backslash.
const PYTHON_ESCAPED_CHARS: &[char] = &[
    '(', ')', '[', ']', '{', '}', '?', '*', '+', '-', '|', '^', '$', '\\', '.', '&', '~', '#', ' ', '\t', '\n', '\r', '\u{b}', '\u{c}',
];

/// Characters a path parameter value consists of, apart from the slash, as a regex class body.
const PARAMETER_CHARS: &str = r"\w \$\.\-:\|=~\^%@\+,;!\(\)";

/// The slash, added to the parameter class of a channel whose parameters match across segments.
const PARAMETER_SLASH: &str = "/";

/// Pattern that stands in the Accept slot for a channel accepting any media type.
const ACCEPT_ANY_PATTERN: &str = "[^:]*";

/// End of every compiled target, equivalent to `$` of Python, which also matches before one final newline.
const TARGET_END: &str = r"\n?\z";

/// Python expression that finds path parameters in a pattern, as written in `Matcher` of `url_dispatcher`.
const PYTHON_BRACE_PATTERN: &str = r"\{[\w \$.\-:|=~^/]+\}";

/// What defines one REST channel for the purpose of matching.
pub struct ChannelSpec<'spec> {
    /// HTTP method of the channel, empty if the channel accepts any of the allowed methods.
    pub method: &'spec str,

    /// Accept header value the channel requires, if any.
    pub http_accept: Option<&'spec str>,

    /// URL path of the channel, with path parameters in braces.
    pub url_path: &'spec str,

    /// Whether path parameters match values that span several path segments.
    pub match_slash: bool,
}

/// Reason why a channel cannot be matched by the Rust router with the semantics of the Python matcher.
#[derive(Debug)]
pub enum PatternError {
    /// The match target of the channel is not the one its definition produces.
    TargetMismatch,

    /// The HTTP method is not a plain token.
    UnsupportedMethod,

    /// The URL path contains braces or markers whose Python interpretation is not reproduced.
    UnsupportedPath,

    /// The compiled expression was rejected by the regex engine.
    Regex(regex::Error),
}

impl fmt::Display for PatternError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::TargetMismatch => formatter.write_str("match target differs from the channel definition"),
            Self::UnsupportedMethod => formatter.write_str("HTTP method is not a plain token"),
            Self::UnsupportedPath => formatter.write_str("URL path is not supported"),
            Self::Regex(error) => write!(formatter, "invalid expression: {error}"),
        }
    }
}

/// One piece of a channel URL path.
enum PathPiece<'path> {
    /// Text matched literally.
    Literal(&'path str),

    /// A path parameter, given by its name.
    Parameter(&'path str),
}

/// Returns the text with every character that `re.escape` of Python escapes preceded by a backslash.
pub fn python_re_escape(text: &str) -> String {
    let mut out = String::with_capacity(text.len());

    for character in text.chars() {
        if PYTHON_ESCAPED_CHARS.contains(&character) {
            out.push('\\');
        }
        out.push(character);
    }

    out
}

/// Splits a channel URL path into literal text and path parameters, the way `_escape_url_path` walks it.
fn split_url_path(url_path: &str) -> Vec<PathPiece<'_>> {
    let mut out = Vec::new();
    let mut rest = url_path;

    // Once nothing opens a parameter, or a parameter is never closed, the rest is literal
    while let Some(start) = rest.find('{') {
        let Some(end_offset) = rest.get(start..).and_then(|tail| tail.find('}')) else {
            break;
        };
        let end = start + end_offset;

        let (literal, tail) = rest.split_at(start);
        let (parameter, after) = tail.split_at(end - start + 1);

        // The text between the first opening brace and the first closing one is the name, whatever it contains
        let name = parameter
            .strip_prefix('{')
            .and_then(|inner| inner.strip_suffix('}'))
            .unwrap_or(parameter);

        out.push(PathPiece::Literal(literal));
        out.push(PathPiece::Parameter(name));
        rest = after;
    }

    out.push(PathPiece::Literal(rest));
    out
}

/// Returns the URL path with its literal parts escaped and its parameters left as they are.
pub fn escape_url_path(url_path: &str) -> String {
    let mut out = String::with_capacity(url_path.len());

    for piece in split_url_path(url_path) {
        match piece {
            PathPiece::Literal(text) => out.push_str(&python_re_escape(text)),
            PathPiece::Parameter(name) => {
                out.push('{');
                out.push_str(name);
                out.push('}');
            }
        }
    }

    out
}

/// Returns the method slot of a channel that names no method of its own.
pub fn methods_allowed_pattern(methods_allowed: &[String]) -> String {
    format!("(?:{})", methods_allowed.join("|"))
}

/// Returns the match target of a channel, as `get_match_target` of Python builds it.
pub fn get_match_target(spec: &ChannelSpec<'_>, methods_allowed: &[String]) -> String {
    let method_slot = if spec.method.is_empty() {
        methods_allowed_pattern(methods_allowed)
    } else {
        spec.method.to_owned()
    };

    let accept = python_re_escape(&to_internal_accept(spec.http_accept));
    let url_path = escape_url_path(spec.url_path);

    format!("{TARGET_SEPARATOR}{method_slot}{TARGET_SEPARATOR}{accept}{TARGET_SEPARATOR}{url_path}")
}

/// Whether a method name is a plain token, which Python inserts into the expression without escaping.
fn is_method_token(method: &str) -> bool {
    !method.is_empty()
        && method
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-' || byte == b'_')
}

/// Whether a path parameter name is one that both engines accept as a group name.
fn is_parameter_name(name: &str) -> bool {
    !name.is_empty() && name.chars().all(|character| character.is_alphanumeric() || character == '_')
}

/// Returns the expression of Python that finds path parameters in a pattern.
fn python_brace_regex() -> Result<&'static Regex, PatternError> {
    static BRACE_REGEX: OnceLock<Result<Regex, regex::Error>> = OnceLock::new();

    BRACE_REGEX
        .get_or_init(|| Regex::new(PYTHON_BRACE_PATTERN))
        .as_ref()
        .map_err(|error| PatternError::Regex(error.clone()))
}

/// The compiled form of one channel's match target.
pub struct ChannelPattern {
    /// Expression matched against the targets built from requests.
    regex: Regex,

    /// Names of the path parameters, in the order of their capture groups.
    parameter_names: Vec<String>,

    /// Whether the channel is at an internal `/zato/` path.
    is_internal: bool,
}

impl ChannelPattern {
    /// Compiles the match target of a channel, verifying first that the target is what its definition produces.
    pub fn compile(spec: &ChannelSpec<'_>, methods_allowed: &[String], match_target: &str) -> Result<Self, PatternError> {
        // The expression is built from the definition, so the target it stands for has to be the one in use
        if get_match_target(spec, methods_allowed) != match_target {
            return Err(PatternError::TargetMismatch);
        }

        let mut source = String::from("^");
        source.push_str(TARGET_SEPARATOR);
        source.push_str(&method_source(spec.method, methods_allowed)?);
        source.push_str(TARGET_SEPARATOR);
        source.push_str(&accept_source(spec.http_accept));
        source.push_str(TARGET_SEPARATOR);

        let parameter_names = push_path_source(&mut source, spec)?;
        verify_python_parameters(match_target, &parameter_names)?;

        source.push_str(TARGET_END);

        let regex = Regex::new(&source).map_err(PatternError::Regex)?;

        Ok(Self {
            regex,
            parameter_names,
            is_internal: match_target.contains(INTERNAL_PATH_INDICATOR),
        })
    }

    /// Matches a request target, returning the path parameters by name, empty for a static path.
    pub fn match_target(&self, target: &str) -> Option<Vec<(String, String)>> {
        let captures = self.regex.captures(target)?;
        let mut out = Vec::with_capacity(self.parameter_names.len());

        for (index, name) in self.parameter_names.iter().enumerate() {
            let value = captures.get(index + 1).map_or("", |group| group.as_str());
            out.push((name.clone(), value.to_owned()));
        }

        Some(out)
    }

    /// Whether the channel is at an internal `/zato/` path, which requests for user paths skip.
    pub const fn is_internal(&self) -> bool {
        self.is_internal
    }

    /// Returns the names of the path parameters, in the order the channel defines them.
    pub fn parameter_names(&self) -> &[String] {
        &self.parameter_names
    }
}

/// Returns the regex source of the method slot.
fn method_source(method: &str, methods_allowed: &[String]) -> Result<String, PatternError> {
    if !method.is_empty() {
        if !is_method_token(method) {
            return Err(PatternError::UnsupportedMethod);
        }
        return Ok(regex::escape(method));
    }

    let mut alternatives = Vec::with_capacity(methods_allowed.len());

    for allowed in methods_allowed {
        if !is_method_token(allowed) {
            return Err(PatternError::UnsupportedMethod);
        }
        alternatives.push(regex::escape(allowed));
    }

    Ok(format!("(?:{})", alternatives.join("|")))
}

/// Returns the regex source of the Accept slot, where each `*/*` stands for any value without a separator.
fn accept_source(http_accept: Option<&str>) -> String {
    let internal = to_internal_accept(http_accept);
    let mut pieces = Vec::new();

    for piece in internal.split(ACCEPT_ANY_PAIR) {
        pieces.push(regex::escape(piece));
    }

    pieces.join(ACCEPT_ANY_PATTERN)
}

/// Appends the regex source of the URL path and returns the names of its parameters.
fn push_path_source(source: &mut String, spec: &ChannelSpec<'_>) -> Result<Vec<String>, PatternError> {
    // The any-value marker in a path would be rewritten by the Python matcher as well
    if spec.url_path.contains(ACCEPT_ANY_PAIR) {
        return Err(PatternError::UnsupportedPath);
    }

    let slash = if spec.match_slash { PARAMETER_SLASH } else { "" };
    let mut names: Vec<String> = Vec::new();
    let mut seen: HashSet<&str> = HashSet::new();

    for piece in split_url_path(spec.url_path) {
        match piece {
            PathPiece::Literal(text) => source.push_str(&regex::escape(text)),
            PathPiece::Parameter(name) => {
                // A repeated name or a name outside of the word characters is read differently by the two engines
                if !is_parameter_name(name) || !seen.insert(name) {
                    return Err(PatternError::UnsupportedPath);
                }
                source.push_str("([");
                source.push_str(PARAMETER_CHARS);
                source.push_str(slash);
                source.push_str("]+)");
                names.push(name.to_owned());
            }
        }
    }

    Ok(names)
}

/// Verifies that the Python matcher finds exactly the same path parameters in the match target.
fn verify_python_parameters(match_target: &str, names: &[String]) -> Result<(), PatternError> {
    let brace_regex = python_brace_regex()?;
    let mut found = brace_regex.find_iter(match_target).map(|found_match| found_match.as_str());

    for name in names {
        let expected = format!("{{{name}}}");
        if found.next() != Some(expected.as_str()) {
            return Err(PatternError::UnsupportedPath);
        }
    }

    if found.next().is_some() {
        return Err(PatternError::UnsupportedPath);
    }

    Ok(())
}
