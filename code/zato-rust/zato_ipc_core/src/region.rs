//! Creation of the shared memory region in an anonymous memory file.
//!
//! The arbiter creates the region before it forks the worker and the config process, so both inherit
//! the mapping at the same address. The memory file has no name in the file system,
//! so the size limit of `/dev/shm` in containers does not apply to it.

use std::os::fd::OwnedFd;
use std::sync::atomic::AtomicU64;

use rustix::fs::{MemfdFlags, ftruncate, memfd_create};
use rustix::mm::{MapFlags, ProtFlags, mmap};

use crate::error::RegionError;
use crate::layout::{Layout, RegionParams};
use crate::view::RegionView;

/// Name of the memory file, as `/proc/<pid>/maps` lists it.
const MEMORY_FILE_NAME: &str = "zato-shared-region";

/// The shared memory region of one server, mapped for the lifetime of the process.
#[derive(Debug)]
pub struct Region {

    /// The memory file behind the mapping.
    memory_file: OwnedFd,

    /// Every word of the mapping.
    words: &'static [AtomicU64],

    /// Offsets of the tables within `words`.
    layout: Layout,
}

/// Maps the whole memory file and returns its words.
///
/// The mapping is never unmapped, because the region serves the process until it exits.
fn map_words(memory_file: &OwnedFd, layout: &Layout) -> Result<&'static [AtomicU64], RegionError> {
    let byte_count = layout.total_bytes()?;

    #[expect(unsafe_code, reason = "mapping a memory file has no safe interface")]
    // SAFETY: the address is chosen by the kernel, so the mapping overlaps no existing memory of the process,
    // and the length equals the size given to `ftruncate`, so every mapped page is backed by the file.
    let address = unsafe {
        mmap(
            std::ptr::null_mut(),
            byte_count,
            ProtFlags::READ | ProtFlags::WRITE,
            MapFlags::SHARED,
            memory_file,
            0,
        )
    }?;

    #[expect(unsafe_code, reason = "a slice over mapped memory has no safe constructor")]
    // SAFETY: the mapping is page-aligned, which satisfies the alignment of `AtomicU64`, it is `total_words` words long,
    // the file starts zero-filled, which is a valid value of every word, and it is never unmapped, so it lives
    // for the rest of the process. Every access goes through atomic operations, which permit sharing between
    // processes and threads alike.
    let words = unsafe { std::slice::from_raw_parts(address.cast::<AtomicU64>(), layout.total_words) };

    Ok(words)
}

impl Region {

    /// Creates the region of a server with the given table sizes.
    pub fn create(params: RegionParams) -> Result<Self, RegionError> {
        let layout = Layout::new(params)?;
        let byte_count = u64::try_from(layout.total_bytes()?).map_err(|_conversion_error| RegionError::LayoutTooLarge)?;

        // The worker and the config process inherit the descriptor at fork, and no program the server starts later needs it.
        let memory_file = memfd_create(MEMORY_FILE_NAME, MemfdFlags::CLOEXEC)?;
        ftruncate(&memory_file, byte_count)?;

        let words = map_words(&memory_file, &layout)?;
        layout.write_header(words)?;

        let out = Self {
            memory_file,
            words,
            layout,
        };
        Ok(out)
    }

    /// Returns a view of the tables of the region.
    pub const fn view(&self) -> Result<RegionView<'static>, RegionError> {
        RegionView::new(self.words, self.layout)
    }

    /// Returns the memory file behind the region.
    #[must_use]
    pub const fn memory_file(&self) -> &OwnedFd {
        &self.memory_file
    }

    /// Confirms that the header of the region describes the layout this build of the crate uses.
    pub fn verify(&self) -> Result<(), RegionError> {
        self.layout.verify_header(self.words)
    }
}

#[cfg(test)]
mod tests {
    use std::sync::atomic::Ordering;

    use super::*;
    use crate::layout::{BLOCK_WORDS, BYTES_PER_WORD, HEADER_VERSION};
    use crate::view::test_support::small_params;

    #[test]
    fn created_region_has_a_valid_header() -> Result<(), RegionError> {
        let region = Region::create(small_params())?;

        region.verify()?;

        Ok(())
    }

    #[test]
    fn region_starts_at_a_block_boundary() -> Result<(), RegionError> {
        let region = Region::create(small_params())?;

        // The offsets of the layout align each entry to a block only if the mapping itself starts at one
        let block_bytes = BLOCK_WORDS * BYTES_PER_WORD;
        assert_eq!(region.words.as_ptr().addr() % block_bytes, 0);

        Ok(())
    }

    #[test]
    fn changed_header_is_detected() -> Result<(), RegionError> {
        let region = Region::create(small_params())?;
        let view = region.view()?;

        view.word(HEADER_VERSION)?.store(99, Ordering::SeqCst);

        assert_eq!(region.verify(), Err(RegionError::LayoutMismatch("layout version")));

        Ok(())
    }

    #[test]
    fn region_is_shared_with_a_second_mapping() -> Result<(), RegionError> {
        let region = Region::create(small_params())?;
        let second = map_words(region.memory_file(), &region.layout)?;
        let second_view = RegionView::new(second, region.layout)?;

        region.view()?.set_heartbeat(1_794_000_000)?;

        assert_eq!(second_view.heartbeat()?, 1_794_000_000);

        Ok(())
    }
}
