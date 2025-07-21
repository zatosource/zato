# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import random
import time
from datetime import datetime, timedelta

# Zato
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

def get_remaining_time(start_time:'datetime', max_seconds:'int') -> 'float':
    """ Calculate remaining time in seconds based on start time and maximum duration.
    """
    max_duration = timedelta(seconds=max_seconds)
    elapsed = utcnow() - start_time
    remaining = max_duration - elapsed

    return max(0, remaining.total_seconds())

# ################################################################################################################################
# ################################################################################################################################

def get_sleep_time(
    start_time: 'datetime',
    max_seconds: 'int',
    attempt_number: 'int',
    jitter_range: 'float' = 2.0
) -> 'float':
    """ Get sleep time for the given attempt number.
    """

    # Calculate remaining time
    time_remaining_seconds = get_remaining_time(start_time, max_seconds)

    # No sleep before first attempt or if time is up
    if attempt_number <= 1 or time_remaining_seconds <= 0:
        return 0.0

    # Initial attempts get 5 seconds, and later it's 10 seconds.
    # We'll add jittter in either case later on.
    if attempt_number <= 12:
         base_sleep = 5.0
    else:
         base_sleep = 10.0

    # Add jitter
    jitter = random.uniform(0, jitter_range)
    final_sleep = base_sleep + jitter

    # Check if we have time for this sleep
    if final_sleep > time_remaining_seconds:
        return 0.0

    return final_sleep

# ################################################################################################################################
# ################################################################################################################################

def simulate_sleep_times() -> 'None':
   """ Simulate sleep times for different attempt numbers.
   """
   print('Sleep Time Simulation:')
   print('Attempt | Sleep Time | Range')
   print('-' * 35)

   # Show key attempts that demonstrate the algorithm
   key_attempts = [1, 2, 5, 10, 12, 13, 15, 20, 50, 100]

   # Use a dummy start time and long duration for simulation
   dummy_start = utcnow()

   for attempt in key_attempts:
       sleep_time = get_sleep_time(dummy_start, 48*3600, attempt, jitter_range=0.0)  # No jitter for preview

       # Determine which range this falls into
       if attempt <= 1:
           range_desc = 'No sleep'
       elif attempt <= 12:
           range_desc = '2-12 (5s base)'
       else:
           range_desc = '13+ (10s base)'

       print(f'{attempt:7d} | {sleep_time:8.2f}s | {range_desc}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

   # Preview the sleep times
   simulate_sleep_times()

   print('\n' + '='*50)
   print('SIMULATION: First 15 attempts over 48 seconds')
   print('='*50)

   # Start the timer
   start_time = utcnow()
   max_seconds = 48*3600
   attempt = 0

   # Simulate first 15 API calls
   for idx in range(15):
       attempt += 1

       # Calculate remaining time
       remaining_seconds = get_remaining_time(start_time, max_seconds)
       remaining_hours = remaining_seconds / 3600

       print(f'\nAttempt {attempt}:')
       print(f'  Time remaining: {remaining_hours:.1f} hours')

       print(f'  Making API call #{attempt}...')


        # Don't sleep after the last demo attempt
       if idx < 14:
           sleep_time = get_sleep_time(start_time, max_seconds, attempt + 1)

           if sleep_time == 0:
               elapsed = utcnow() - start_time
               if elapsed >= timedelta(seconds=max_seconds):
                   print('  Time limit reached!')
                   break
               else:
                   print('  No sleep needed (first attempt)')
           else:
               print(f'  Sleeping for {sleep_time:.2f}s before next attempt...')
               time.sleep(sleep_time)

   print(f'\nFinal stats after {attempt} attempts:')

   remaining_seconds = get_remaining_time(start_time, max_seconds)
   remaining_hours = remaining_seconds / 3600
   elapsed_hours = max_seconds / 3600 - remaining_hours

   print(f'  Elapsed: {elapsed_hours:.3f} hours')
   print(f'  Remaining: {remaining_hours:.1f} hours')

# ################################################################################################################################
# ################################################################################################################################
