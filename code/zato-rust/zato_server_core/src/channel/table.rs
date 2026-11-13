//! Ordered table of REST channels that request targets are matched against.
//!
//! The order of the table is the order of the channel list of `URLData`, user channels first,
//! and the first channel that matches handles the request, exactly as `PyURLData.match` decides.

use std::collections::{BTreeSet, HashSet};

use super::lru::LruCache;
use super::matcher::{ChannelPattern, TARGET_SEPARATOR};
use super::path::to_internal_accept;

/// Number of request targets remembered in each of the hit and miss caches.
pub const TARGET_CACHE_SIZE: usize = 10_000;

/// Path prefix of internal Zato channels, which requests for other paths never reach.
const INTERNAL_PATH_PREFIX: &str = "/zato";

/// One channel of the table.
pub struct TableEntry<T> {
    /// Compiled match target of the channel.
    pub pattern: ChannelPattern,

    /// HTTP method of the channel, empty if it accepts any allowed method.
    pub method: String,

    /// Internal form of the Accept value of the channel.
    pub accept_internal: String,

    /// Data the owner of the table keeps for the channel.
    pub payload: T,
}

/// A channel that matched a request, with the path parameters taken from the request.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MatchedChannel {
    /// Position of the channel in the table.
    pub index: usize,

    /// Path parameters by name, in the order the channel defines them.
    pub parameters: Vec<(String, String)>,
}

/// Ordered channel table with the hit and miss caches of `PyURLData`.
pub struct ChannelTable<T> {
    /// Channels in matching order.
    entries: Vec<TableEntry<T>>,

    /// Internal forms of every Accept value that some channel names.
    channel_accepts: HashSet<String>,

    /// Targets that matched a channel.
    hits: LruCache<MatchedChannel>,

    /// Targets that matched no channel, with the methods their path accepts.
    misses: LruCache<BTreeSet<String>>,

    /// Internal form of `*/*`, which a request Accept value no channel names is matched as.
    accept_any: String,
}

impl<T> ChannelTable<T> {
    /// Returns a table of the channels in the order given.
    pub fn new(entries: Vec<TableEntry<T>>) -> Self {
        let mut channel_accepts = HashSet::new();

        for entry in &entries {
            channel_accepts.insert(entry.accept_internal.clone());
        }

        Self {
            entries,
            channel_accepts,
            hits: LruCache::new(TARGET_CACHE_SIZE),
            misses: LruCache::new(TARGET_CACHE_SIZE),
            accept_any: to_internal_accept(None),
        }
    }

    /// Returns the channel at a position of the table.
    pub fn entry(&self, index: usize) -> Option<&TableEntry<T>> {
        self.entries.get(index)
    }

    /// Returns the number of channels.
    pub const fn len(&self) -> usize {
        self.entries.len()
    }

    /// Whether the table has no channels.
    pub const fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    /// Returns the Accept value a request is matched with, which is its own if some channel names it.
    fn bucket_accept(&self, accept_internal: &str) -> String {
        if self.channel_accepts.contains(accept_internal) {
            accept_internal.to_owned()
        } else {
            self.accept_any.clone()
        }
    }

    /// Finds the channel handling a request, given its normalized path, method and internal Accept value.
    pub fn find(&mut self, path: &str, method: &str, accept_internal: &str) -> Option<MatchedChannel> {
        let accept = self.bucket_accept(accept_internal);
        let target = build_target(method, &accept, path);

        if let Some(cached) = self.hits.get(&target) {
            return Some(cached.clone());
        }

        // A target known to match nothing is only marked as recently used
        if self.misses.get(&target).is_some() {
            return None;
        }

        let skips_internal = !path.starts_with(INTERNAL_PATH_PREFIX);
        let mut method_entries: Vec<usize> = Vec::new();

        for (index, entry) in self.entries.iter().enumerate() {
            if skips_internal && entry.pattern.is_internal() {
                continue;
            }

            if let Some(parameters) = entry.pattern.match_target(&target) {
                let matched = MatchedChannel { index, parameters };
                self.hits.insert(target, matched.clone());
                return Some(matched);
            }

            if !entry.method.is_empty() {
                method_entries.push(index);
            }
        }

        let allowed = self.allow_methods_from(&method_entries, path, &accept);
        self.misses.insert(target, allowed);

        None
    }

    /// Returns the methods with which some channel accepts the path, for the Allow header of a 405 response.
    pub fn allow_methods(&self, path: &str, method: &str, accept_internal: &str) -> BTreeSet<String> {
        let accept = self.bucket_accept(accept_internal);
        let target = build_target(method, &accept, path);

        if let Some(cached) = self.misses.peek(&target) {
            return cached.clone();
        }

        let skips_internal = !path.starts_with(INTERNAL_PATH_PREFIX);
        let mut method_entries: Vec<usize> = Vec::new();

        for (index, entry) in self.entries.iter().enumerate() {
            if skips_internal && entry.pattern.is_internal() {
                continue;
            }
            if !entry.method.is_empty() {
                method_entries.push(index);
            }
        }

        self.allow_methods_from(&method_entries, path, &accept)
    }

    /// Returns the methods of the given channels whose target with their own method matches the path.
    fn allow_methods_from(&self, method_entries: &[usize], path: &str, accept: &str) -> BTreeSet<String> {
        let mut out = BTreeSet::new();

        for index in method_entries {
            let Some(entry) = self.entries.get(*index) else { continue };
            let target = build_target(&entry.method, accept, path);

            if entry.pattern.match_target(&target).is_some() {
                out.insert(entry.method.clone());
            }
        }

        out
    }

    /// Returns the payloads of all channels, in matching order.
    pub fn payloads(&self) -> impl Iterator<Item = &T> {
        self.entries.iter().map(|entry| &entry.payload)
    }
}

/// Returns the target a request is matched as.
fn build_target(method: &str, accept: &str, path: &str) -> String {
    let mut out = String::with_capacity(method.len() + accept.len() + path.len() + TARGET_SEPARATOR.len() * 3);
    out.push_str(TARGET_SEPARATOR);
    out.push_str(method);
    out.push_str(TARGET_SEPARATOR);
    out.push_str(accept);
    out.push_str(TARGET_SEPARATOR);
    out.push_str(path);
    out
}
