# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from multiprocessing import get_context

# pytest
import pytest

# Zato
from zato.common.worker_count import get_affinity_count, get_worker_cpus, resolve_worker_count, ServerWorkers, \
    WorkerCountError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import intlist, intnone

    intlist = intlist
    intnone = intnone
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The number of CPUs that the process of most tests may run on
    Affinity_Count = 8

    # The period of the synthetic quotas, in microseconds
    Period = 100_000

    # How long the test waits for its forked process, in seconds
    Join_Timeout = 30.0

# ################################################################################################################################
# ################################################################################################################################

def _write_cpu_max(tmp_path:'Path', contents:'str') -> 'str':
    path = tmp_path / 'cpu.max'
    _ = path.write_text(contents)

    out = str(path)
    return out

# ################################################################################################################################

def _resolve_auto(cpu_max_path:'str') -> 'int':
    out = resolve_worker_count(ServerWorkers.Auto, None, ModuleCtx.Affinity_Count, cpu_max_path)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_auto_without_a_cgroup_file_is_the_affinity_count(tmp_path:'Path') -> 'None':
    cpu_max_path = str(tmp_path / 'no-such-cpu.max')
    assert _resolve_auto(cpu_max_path) == ModuleCtx.Affinity_Count

# ################################################################################################################################

def test_auto_without_a_quota_is_the_affinity_count(tmp_path:'Path') -> 'None':
    cpu_max_path = _write_cpu_max(tmp_path, f'max {ModuleCtx.Period}\n')
    assert _resolve_auto(cpu_max_path) == ModuleCtx.Affinity_Count

# ################################################################################################################################

@pytest.mark.parametrize(('quota', 'expected'), [
    (200_000, 2),
    (150_000, 2),
    (50_000, 1),
    (800_000, 8),
    (1_600_000, 8),
])
def test_auto_is_the_smaller_of_the_quota_rounded_up_and_the_affinity_count(
    tmp_path:'Path',
    quota:'int',
    expected:'int',
    ) -> 'None':

    cpu_max_path = _write_cpu_max(tmp_path, f'{quota} {ModuleCtx.Period}\n')
    assert _resolve_auto(cpu_max_path) == expected

# ################################################################################################################################

def test_an_integer_is_used_as_it_is(tmp_path:'Path') -> 'None':
    cpu_max_path = _write_cpu_max(tmp_path, f'100000 {ModuleCtx.Period}\n')

    out = resolve_worker_count('3', None, ModuleCtx.Affinity_Count, cpu_max_path)
    assert out == 3

# ################################################################################################################################

def test_the_environment_overrides_server_conf(tmp_path:'Path') -> 'None':
    cpu_max_path = _write_cpu_max(tmp_path, f'200000 {ModuleCtx.Period}\n')

    # An integer in the environment replaces the one in server.conf ..
    out = resolve_worker_count('2', '5', ModuleCtx.Affinity_Count, cpu_max_path)
    assert out == 5

    # .. as auto does ..
    out = resolve_worker_count('6', ServerWorkers.Auto, ModuleCtx.Affinity_Count, cpu_max_path)
    assert out == 2

    # .. and an empty variable leaves server.conf in effect.
    out = resolve_worker_count('6', '', ModuleCtx.Affinity_Count, cpu_max_path)
    assert out == 6

# ################################################################################################################################

def test_a_server_conf_without_the_key_resolves_to_auto(tmp_path:'Path') -> 'None':
    cpu_max_path = _write_cpu_max(tmp_path, f'300000 {ModuleCtx.Period}\n')

    out = resolve_worker_count(None, None, ModuleCtx.Affinity_Count, cpu_max_path)
    assert out == 3

# ################################################################################################################################

@pytest.mark.parametrize('value', ['0', '-1', '1.5', 'two', '', ' ', '\u00b2', 'auto1'])
def test_an_invalid_value_is_rejected(tmp_path:'Path', value:'str') -> 'None':
    cpu_max_path = _write_cpu_max(tmp_path, f'max {ModuleCtx.Period}\n')

    with pytest.raises(WorkerCountError):
        _ = resolve_worker_count(value, None, ModuleCtx.Affinity_Count, cpu_max_path)

# ################################################################################################################################

def _resolve_under_one_cpu(cpu_max_path:'str', output_path:'str') -> 'None':
    exit_code = 1

    try:

        # The process may run on its first CPU only ..
        cpus = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, {cpus[0]})

        # .. so auto resolves to one worker.
        affinity_count = get_affinity_count()
        out = resolve_worker_count(ServerWorkers.Auto, None, affinity_count, cpu_max_path)

        with open(output_path, 'w') as output:
            _ = output.write(str(out))

        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def test_auto_follows_the_affinity_mask(tmp_path:'Path') -> 'None':
    cpu_max_path = str(tmp_path / 'no-such-cpu.max')
    output_path = str(tmp_path / 'count')

    context = get_context('fork')

    process = context.Process(target=_resolve_under_one_cpu, args=(cpu_max_path, output_path))
    process.start()
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

    with open(output_path) as output:
        assert output.read() == '1'

# ################################################################################################################################

def test_as_many_workers_as_cpus_are_pinned_by_the_position_of_their_slots() -> 'None':
    out = get_worker_cpus(3, [9, 2, 5], None)
    assert out == [2, 5, 9]

# ################################################################################################################################

@pytest.mark.parametrize(('worker_count', 'cpu_limit', 'expected'), [
    (2, None, []),
    (4, None, []),
    (3, 2, []),
    (3, 1, []),
    (3, 3, [2, 5, 9]),
    (3, 4, [2, 5, 9]),
])
def test_no_worker_is_pinned_unless_the_count_and_the_quota_cover_every_cpu(
    worker_count:'int',
    cpu_limit:'intnone',
    expected:'intlist',
    ) -> 'None':

    out = get_worker_cpus(worker_count, [9, 2, 5], cpu_limit)
    assert out == expected

# ################################################################################################################################
# ################################################################################################################################
