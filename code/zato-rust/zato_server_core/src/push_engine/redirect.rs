//! The redirects that a push follows.
//!
//! Only 307 and 308 are followed, because they keep the method and the body, at most `MAX_PUSH_REDIRECTS` times,
//! within the network scope of the first push, which must be public, private or loopback. The Location
//! of a redirect is resolved against the current address the way `urllib.parse.urljoin` resolves it,
//! and the next address must be an `http` or `https` address with a host, a valid port and no user information,
//! never `http` after `https`.

use crate::outgoing::scope::NetworkScope;

/// How many redirects one attempt of a push follows.
pub const MAX_PUSH_REDIRECTS: usize = 5;

/// The status of a temporary redirect that keeps the method and the body.
pub const TEMPORARY_REDIRECT: u16 = 307;

/// The status of a permanent redirect that keeps the method and the body.
pub const PERMANENT_REDIRECT: u16 = 308;

/// The lowest character of a Location value, which excludes whitespace and control characters.
const LOCATION_CHAR_MIN: u8 = 0x21;

/// The highest character of a Location value, which excludes non-ASCII characters.
const LOCATION_CHAR_MAX: u8 = 0x7e;

/// The scheme of a plain HTTP address.
const SCHEME_HTTP: &str = "http";

/// The scheme of an HTTPS address.
const SCHEME_HTTPS: &str = "https";

/// The lowest port of an address.
const PORT_MIN: u32 = 1;

/// The highest port of an address.
const PORT_MAX: u32 = 65_535;

/// The radix of the digits of a port.
const DECIMAL_RADIX: u32 = 10;

/// Returns the address that a response to a push redirects to, or `None` for a response that is not a redirect
/// to be followed, or the reason why a redirect is not followed.
///
/// The location is the value of the Location header of the response, if it has one.
pub fn next_redirect(
    url: &str,
    status: u16,
    location: Option<&str>,
    hop_count: usize,
    first_scope: Option<NetworkScope>,
) -> Result<Option<String>, String> {
    // Only the statuses that keep the method and the body are followed ..
    if status != TEMPORARY_REDIRECT && status != PERMANENT_REDIRECT {
        return Ok(None);
    }

    // .. within the network scope of the first push of the attempt ..
    let scope_name = first_scope.map_or("None", NetworkScope::name);

    if !matches!(first_scope, Some(NetworkScope::Public | NetworkScope::Private | NetworkScope::Loopback)) {
        return Err(format!("Redirect {status} from `{url}` in the network scope `{scope_name}` is not followed"));
    }

    // .. up to a fixed number of times ..
    if hop_count >= MAX_PUSH_REDIRECTS {
        return Err(format!(
            "Redirect {status} from `{url}` beyond the limit of {MAX_PUSH_REDIRECTS} redirects"
        ));
    }

    // .. to the address the redirect names ..
    let Some(location) = location.filter(|value| !value.is_empty()) else {
        return Err(format!("Redirect {status} from `{url}` without a Location header"));
    };

    check_location(location)?;

    let out = resolve_location(url, location)?;

    // .. never using HTTP after HTTPS.
    let current_scheme = split_scheme(url).map(|(scheme, _)| scheme.to_ascii_lowercase());
    let next_scheme = split_scheme(&out).map(|(scheme, _)| scheme.to_ascii_lowercase());

    if current_scheme.as_deref() == Some(SCHEME_HTTPS) && next_scheme.as_deref() == Some(SCHEME_HTTP) {
        return Err(format!("Redirect {status} from `{url}` to `{out}` uses HTTP after HTTPS"));
    }

    Ok(Some(out))
}

/// Rejects a Location value that contains whitespace, control characters or characters outside ASCII.
fn check_location(location: &str) -> Result<(), String> {
    let is_valid = location.bytes().all(|byte| (LOCATION_CHAR_MIN..=LOCATION_CHAR_MAX).contains(&byte));

    if is_valid {
        Ok(())
    } else {
        Err(format!("Redirect to {location:?} with a character outside of the range of a Location"))
    }
}

/// The parts of an address that a reference is resolved against and that the next address is built from.
struct UrlParts<'url> {

    /// The scheme, as written.
    scheme: &'url str,

    /// The authority, `None` if the address has none.
    authority: Option<&'url str>,

    /// The path.
    path: String,

    /// The query string without its question mark, `None` if the address has none.
    query: Option<&'url str>,
}

/// Splits an address into its scheme and the rest, if it begins with a scheme.
fn split_scheme(url: &str) -> Option<(&str, &str)> {
    let (scheme, rest) = url.split_once(':')?;

    let mut chars = scheme.chars();
    let first = chars.next()?;

    // A scheme starts with a letter and continues with letters, digits and a few marks
    let is_scheme = first.is_ascii_alphabetic() && chars.all(|char| char.is_ascii_alphanumeric() || matches!(char, '+' | '-' | '.'));

    is_scheme.then_some((scheme, rest))
}

/// Splits what follows the scheme into its authority, its path and its query string, the fragment removed.
fn split_hierarchy(rest: &str) -> (Option<&str>, &str, Option<&str>) {
    let without_fragment = rest.split_once('#').map_or(rest, |(before, _)| before);

    let (before_query, query) = match without_fragment.split_once('?') {
        Some((before, query)) => (before, Some(query)),
        None => (without_fragment, None),
    };

    // An authority follows two slashes and ends at the path
    let Some(after_slashes) = before_query.strip_prefix("//") else {
        return (None, before_query, query);
    };

    let authority_end = after_slashes.find('/').unwrap_or(after_slashes.len());
    let (authority, path) = after_slashes.split_at(authority_end);

    (Some(authority), path, query)
}

/// Parses an absolute address into its parts.
fn parse_parts(url: &str) -> Option<UrlParts<'_>> {
    let (scheme, rest) = split_scheme(url)?;
    let (authority, path, query) = split_hierarchy(rest);

    Some(UrlParts {
        scheme,
        authority,
        path: path.to_owned(),
        query,
    })
}

/// Resolves a Location value against the current address and returns the next address, without a fragment,
/// or the reason why it is not a valid address of an HTTP or HTTPS endpoint.
fn resolve_location(url: &str, location: &str) -> Result<String, String> {
    let base = parse_parts(url).ok_or_else(|| format!("Redirect from `{url}`, which is not an absolute address"))?;
    let joined = join(&base, location);

    let parts = parse_parts(&joined).ok_or_else(|| format!("Redirect to `{location}` with a scheme other than http and https"))?;

    // A scheme in upper case is accepted and lowercased ..
    let scheme = parts.scheme.to_ascii_lowercase();

    if scheme != SCHEME_HTTP && scheme != SCHEME_HTTPS {
        return Err(format!("Redirect to `{location}` with a scheme other than http and https"));
    }

    let authority = parts.authority.unwrap_or_default();

    // .. user information is not accepted ..
    if authority.contains('@') {
        return Err(format!("Redirect to `{location}` with user information"));
    }

    // .. a host is required, and so is a valid port, if one is given.
    check_authority(location, authority)?;

    let mut out = format!("{scheme}://{authority}");

    // A path that does not start with a slash is given one, as urlunsplit gives it
    if !parts.path.is_empty() && !parts.path.starts_with('/') {
        out.push('/');
    }
    out.push_str(&parts.path);

    if let Some(query) = parts.query.filter(|query| !query.is_empty()) {
        out.push('?');
        out.push_str(query);
    }

    Ok(out)
}

/// Checks that an authority has a host and, if it gives a port, a port from 1 to 65535.
fn check_authority(location: &str, authority: &str) -> Result<(), String> {
    let (host, port) = if let Some(bracketed) = authority.strip_prefix('[') {
        let Some((host, after_host)) = bracketed.split_once(']') else {
            return Err(format!("Redirect to `{location}` with an invalid IPv6 address"));
        };

        let port = match after_host.strip_prefix(':') {
            Some(port) => port,
            None if after_host.is_empty() => "",
            None => return Err(format!("Redirect to `{location}` with an invalid port")),
        };

        (host, port)
    } else {
        authority.split_once(':').unwrap_or((authority, ""))
    };

    if host.is_empty() {
        return Err(format!("Redirect to `{location}` without a host"));
    }

    // An empty port is no port at all, as urllib.parse reads it
    if port.is_empty() {
        return Ok(());
    }

    let is_digits = port.bytes().all(|byte| byte.is_ascii_digit());
    let value = u32::from_str_radix(port, DECIMAL_RADIX).ok().filter(|_| is_digits);

    match value {
        Some(number) if (PORT_MIN..=PORT_MAX).contains(&number) => Ok(()),
        _ => Err(format!("Redirect to `{location}` with an invalid port")),
    }
}

/// Resolves a reference against a base address as `urllib.parse.urljoin` resolves it for HTTP addresses.
fn join(base: &UrlParts<'_>, reference: &str) -> String {
    let base_scheme = base.scheme.to_ascii_lowercase();

    // A reference with a scheme stands on its own, unless it repeats the scheme of the base without an authority ..
    let relative = match split_scheme(reference) {
        Some((scheme, rest)) if scheme.eq_ignore_ascii_case(&base_scheme) && !rest.starts_with("//") => rest,
        Some(_) => return reference.to_owned(),
        None => reference,
    };

    let (authority, path, query) = split_hierarchy(relative);

    // .. a reference with an authority keeps only the scheme of the base ..
    if let Some(authority) = authority {
        return build(&base_scheme, Some(authority), &remove_dot_segments(path), query);
    }

    // .. an empty path keeps the path of the base, and its query string unless the reference gives one ..
    if path.is_empty() {
        let query = query.or(base.query);
        return build(&base_scheme, base.authority, &base.path, query);
    }

    // .. an absolute path replaces the path of the base ..
    if path.starts_with('/') {
        return build(&base_scheme, base.authority, &remove_dot_segments(path), query);
    }

    // .. and a relative path replaces the last segment of the path of the base.
    let directory = base.path.rfind('/').map_or("/", |idx| base.path.get(..=idx).unwrap_or("/"));
    let merged = format!("{directory}{path}");

    build(&base_scheme, base.authority, &remove_dot_segments(&merged), query)
}

/// Builds an address from its parts.
fn build(scheme: &str, authority: Option<&str>, path: &str, query: Option<&str>) -> String {
    let mut out = format!("{scheme}:");

    if let Some(authority) = authority {
        out.push_str("//");
        out.push_str(authority);
    }

    out.push_str(path);

    if let Some(query) = query {
        out.push('?');
        out.push_str(query);
    }

    out
}

/// Removes the `.` and `..` segments of a path, as RFC 3986 section 5.2.4 removes them.
fn remove_dot_segments(path: &str) -> String {
    let mut output: Vec<&str> = Vec::new();
    let segments: Vec<&str> = path.split('/').collect();
    let last_idx = segments.len().saturating_sub(1);

    for (idx, segment) in segments.iter().enumerate() {
        let is_last = idx == last_idx;

        match *segment {
            "." => {
                // A dot at the end leaves the path ending with a slash
                if is_last {
                    output.push("");
                }
            }
            ".." => {
                // The root segment, an empty one at the start of an absolute path, is never removed
                if output.len() > 1 || output.first().is_some_and(|first| !first.is_empty()) {
                    output.pop();
                }
                if is_last {
                    output.push("");
                }
            }
            other => output.push(other),
        }
    }

    output.join("/")
}

#[cfg(test)]
#[path = "redirect_tests.rs"]
mod tests;
