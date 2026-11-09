// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The highest generation a node has seen, kept in its data directory, against which the referee record
//! is checked at startup, so that a referee that lost its data is never written over.

use std::fs::File;
use std::io::{Error, ErrorKind, Write};
use std::path::Path;

/// The suffix of the file written before it replaces the current one.
const NEW_FILE_SUFFIX: &str = ".new";

/// Returns the generation in the file, or zero if the file does not exist.
pub fn read(path: &Path) -> Result<u64, Error> {
    match std::fs::read_to_string(path) {
        Ok(text) => text
            .trim()
            .parse::<u64>()
            .map_err(|error| Error::new(ErrorKind::InvalidData, error)),
        Err(error) if error.kind() == ErrorKind::NotFound => Ok(0),
        Err(error) => Err(error),
    }
}

/// Writes the generation, syncing the file and its directory before it returns.
pub fn write(path: &Path, generation: u64) -> Result<(), Error> {
    let mut new_path = path.as_os_str().to_owned();
    new_path.push(NEW_FILE_SUFFIX);

    let mut file = File::create(&new_path)?;
    file.write_all(generation.to_string().as_bytes())?;
    file.sync_all()?;
    std::fs::rename(&new_path, path)?;

    // The rename is durable only once the directory is synced.
    if let Some(parent) = path.parent() {
        File::open(parent)?.sync_all()?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_missing_file_is_generation_zero() {
        let dir = tempfile::tempdir().unwrap();
        assert_eq!(read(&dir.path().join("ha-generation")).unwrap(), 0);
    }

    #[test]
    fn a_written_generation_is_read_back() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("ha-generation");
        write(&path, 42).unwrap();
        assert_eq!(read(&path).unwrap(), 42);
    }
}
