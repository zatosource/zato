# Adding a protocol to the file transfer schedule suite

Every test in this suite is written once, in `zato.common.test.file_transfer_harness`, and runs against
whatever protocols the suite declares. A protocol is added by writing one adapter class, one session
fixture and one subclass per test module. Nothing in the harness changes.

## 1. The adapter

Write `zato/common/test/file_transfer_harness/<protocol>_adapter.py` with a subclass of `FileTransferAdapter`.
If the test server serves a directory on the machine running the tests, mix in `LocalBackedRemote` as well
and only two of the inspection methods below are left to write. The mixin goes first in the base list,
`class SFTPAdapter(LocalBackedRemote, FileTransferAdapter)`, so that what it supplies wins over the
declarations of the base class.

### Identity and timing

| Attribute | What it says |
| --- | --- |
| `conn_type` | The `GENERIC.CONNECTION.TYPE.*` value of the connections this protocol creates. The job name prefix and the dispatch service follow from it, so they are never declared. |
| `conn_name_prefix` | What every connection a test creates starts with, so the cleanup pass recognises its own leftovers. |
| `settle_timeout` | How long an assertion about the remote side may keep polling, in seconds. A protocol whose writes are visible at once leaves this at zero and nothing waits. |
| `settle_sleep_time` | How long to sleep between two looks while polling, in seconds. |

### Capability flags

A flag that is false skips every test that needs it, so a protocol never fails a test for something it
does not have.

| Flag | What it says |
| --- | --- |
| `supports_claim` | A file can be renamed in place, without which claiming cannot work. |
| `supports_move` | A file can be moved rather than only deleted once its target service is done. |
| `supports_subdirectories` | A directory can hold another directory. |
| `supports_names_with_spaces` | A file name may contain a space. |
| `supports_server_restart` | The test server can be stopped and started again mid-suite. |
| `supports_symlinks` | The remote side has symbolic links at all. |
| `preserves_last_modified` | Two looks at an unchanged file report the same modification time, which is what stability mode compares. Without it only marker mode runs. |
| `is_case_sensitive` | Two names differing only in case are two different files. |

### Methods

Server lifecycle. The first two are called by the session fixture, the rest by the tests that need
the remote side to go away.

- `start_server`
- `stop_server` - ends the suite for this protocol and removes everything the server used
- `restart_server` - the server goes away and comes straight back, dropping every open session
- `pause_server` - the server goes away and stays away, keeping everything it serves
- `resume_server` - a paused server comes back exactly as it was

The protocol-specific half of the connection requests.

- `create_conn_payload`
- `edit_conn_payload`

Path arithmetic and directory creation. `make_directory` returns the directory in the shape a schedule's
`directory` field takes for this protocol, which for SMB means the share prefix is already on it.

- `remote_join`
- `make_directory`
- `make_subdirectory`

Out-of-band inspection, meaning how a test looks at the remote side without going through Zato.

- `write_file`
- `append_file`
- `read_file`
- `list_names`
- `exists`
- `delete_file`
- `make_symlink`, only ever called by protocols that declare `supports_symlinks`

`new_conn_name` is inherited and needs no implementation.

Mixing in `LocalBackedRemote` supplies all of the inspection methods, `remote_join`, `make_directory` and
`make_subdirectory` in terms of two declarations of the adapter's own.

- `local_root` - the directory on this machine the test server serves, set once the server is up
- `remote_directory_for` - the remote path of a directory sitting directly under it
- `to_local` - the path on this machine of something the remote side calls `remote_path`

## 2. The fixture

Add a session-scoped fixture to `conftest.py` next to `sftp_adapter` and `smb_adapter`.

```python
@pytest.fixture(scope='session')
def sharepoint_adapter() -> 'any_':
    adapter = SharePointAdapter()
    adapter.start_server()

    yield adapter

    adapter.stop_server()
```

## 3. The subclasses

One three-line subclass per test module - `test_crud.py`, `test_validation.py`, `test_dispatch.py`,
`test_dispatch_modes.py`, `test_usage.py`, `test_concurrency.py`, `test_robustness.py`, `test_identity.py`
and `test_scheduler_driven.py`.

```python
class TestSharePointCrud(CrudTests):

    @pytest.fixture()
    def adapter(self, sharepoint_adapter:'FileTransferAdapter') -> 'FileTransferAdapter':
        return sharepoint_adapter
```

Anything a protocol has that no other one does goes into a `test_<protocol>_only.py` module of its own,
the way `test_sftp_only.py`, `test_smb_only.py` and `test_ftp_only.py` do.
