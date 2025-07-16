# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import random
import time
from datetime import datetime, timedelta

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

# Hardcoded checkpoints: (attempt_threshold, base_sleep_seconds)
_checkpoints = [
    (1, 0.5),              # First retry: 0.5s
    (2, 1.0),              # Second retry: 1s
    (5, 2.0),              # Attempts 3-5: 2s
    (10, 3.0),             # Attempts 6-10: 3s
    (25, 4.0),             # Attempts 11-25: 4s
    (50, 5.0),             # Attempts 26-50: 5s
    (100, 6.0),            # Attempts 51-100: 6s
    (250, 7.0),            # Attempts 101-250: 7s
    (500, 8.0),            # Attempts 251-500: 8s
    (1000, 9.0),           # Attempts 501-1000: 9s
]

_max_sleep_time = 10.0     # Attempts 1000+: 10s (capped)

_default_jitter_range = 0.8

# ################################################################################################################################
# ################################################################################################################################

def get_sleep_time(
    start_time: 'datetime',
    max_hours: 'int',
    attempt_number: 'int',
    jitter_range: 'float' = _default_jitter_range
) -> 'float':
    """ Get sleep time for the given attempt number.
    """

    # Calculate remaining time
    max_duration = timedelta(hours=max_hours)
    elapsed      = datetime.now() - start_time
    remaining    = max_duration - elapsed

    time_remaining_seconds = max(0, remaining.total_seconds())

    # No sleep before first attempt or if time is up
    if attempt_number <= 1 or time_remaining_seconds <= 0:
        return 0.0

    # Find the appropriate checkpoint
    base_sleep = _max_sleep_time  # Default to max if not found
    for threshold, sleep_time in _checkpoints:
        if attempt_number <= threshold:
            base_sleep = sleep_time
            break

    # Add jitter
    jitter      = random.uniform(-jitter_range, jitter_range)
    final_sleep = max(0.1, base_sleep + jitter)  # Minimum 0.1s

    # Check if we have time for this sleep
    if final_sleep > time_remaining_seconds:
        return 0.0

    return final_sleep

# ################################################################################################################################

def get_retry_stats(
    start_time: 'datetime',
    max_hours: 'int',
    current_attempt: 'int'
) -> 'strdict':
    """ Get current retry statistics.
    """
    elapsed   = datetime.now() - start_time
    remaining = max(0, (timedelta(hours=max_hours) - elapsed).total_seconds())

    next_sleep_time = get_sleep_time(start_time, max_hours, current_attempt + 1)

    out = {
        'attempt': current_attempt,
        'elapsed_hours': elapsed.total_seconds() / 3600,
        'remaining_hours': remaining / 3600,
        'max_hours': max_hours,
        'next_sleep_time': next_sleep_time
    }

    return out

# ################################################################################################################################

def preview_sleep_checkpoints() -> 'None':
    """ Preview what sleep times look like for different attempts.
    """
    print('Sleep Time Checkpoints Preview:')
    print('Attempt | Sleep Time | Checkpoint Range')
    print('-' * 45)

    # Show key attempts that demonstrate each checkpoint
    key_attempts = [1, 2, 3, 6, 11, 26, 51, 101, 251, 501, 1001, 5000]

    # Use a dummy start time and long duration for preview
    dummy_start = datetime.now()

    for attempt in key_attempts:
        sleep_time = get_sleep_time(dummy_start, 48, attempt, jitter_range=0.0)  # No jitter for preview

        # Find which checkpoint this falls into
        range_desc = 'N/A'
        for idx, (threshold, _) in enumerate(_checkpoints):
            if attempt <= threshold:
                if idx == 0:
                    range_desc = f'≤ {threshold}'
                else:
                    prev_threshold = _checkpoints[idx-1][0]
                    range_desc = f'{prev_threshold + 1}-{threshold}'
                break
        else:
            # If we didn't break out of the loop, it's beyond the last checkpoint
            last_threshold = _checkpoints[-1][0]
            range_desc = f'> {last_threshold}'

        print(f'{attempt:7d} | {sleep_time:8.2f}s | {range_desc}')

# ################################################################################################################################
# ################################################################################################################################

# Example usage and testing
if __name__ == '__main__':

    # Preview the checkpoints
    preview_sleep_checkpoints()

    print('\n' + '='*50)
    print('SIMULATION: First 10 attempts over 48 hours')
    print('='*50)

    # Start the timer
    start_time = datetime.now()
    max_hours  = 48
    attempt    = 0

    # Simulate first 10 API calls
    for idx in range(10):
        attempt += 1

        stats = get_retry_stats(start_time, max_hours, attempt)
        print(f'\nAttempt {attempt}:')
        print(f'  Time remaining: {stats["remaining_hours"]:.1f} hours')

        # This would be where you make your API call
        print(f'  Making API call #{attempt}...')

        # Get sleep time for next attempt (if not the last one in this demo)
        if idx < 9:  # Don't sleep after the last demo attempt
            sleep_time = get_sleep_time(start_time, max_hours, attempt + 1)

            if sleep_time == 0:
                elapsed = datetime.now() - start_time
                if elapsed >= timedelta(hours=max_hours):
                    print('  Time limit reached!')
                    break
                else:
                    print('  No sleep needed (first attempt)')
            else:
                print(f'  Sleeping for {sleep_time:.2f}s before next attempt...')
                time.sleep(sleep_time)

    print(f'\nFinal stats after {attempt} attempts:')
    final_stats = get_retry_stats(start_time, max_hours, attempt)
    print(f'  Elapsed: {final_stats["elapsed_hours"]:.3f} hours')
    print(f'  Remaining: {final_stats["remaining_hours"]:.1f} hours')

# ################################################################################################################################
# ################################################################################################################################
