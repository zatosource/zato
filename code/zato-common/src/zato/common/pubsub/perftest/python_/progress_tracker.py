# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt
"""

# stdlib
from threading import Lock

# colorama
from colorama import Fore, Style

# Zato
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

class ProgressTracker:
    """ Tracks progress across all producers.
    """
    def __init__(self, total_producers:'int', total_messages:'int') -> 'None':
        self.total_producers = total_producers
        self.total_messages = total_messages
        self.completed_messages = 0
        self.failed_messages = 0
        self.start_time = utcnow()
        self.lock = Lock()

    def update_progress(self, success:'bool'=True) -> 'None':
        """ Update progress counters.
        """
        with self.lock:
            if success:
                self.completed_messages += 1
            else:
                self.failed_messages += 1
            self._display_progress()

    def _display_progress(self) -> 'None':
        """ Display progress in place.
        """
        current_time = utcnow()
        elapsed_time = current_time - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()

        total_processed = self.completed_messages + self.failed_messages
        percentage = (total_processed / self.total_messages) * 100 if self.total_messages > 0 else 0

        if elapsed_seconds > 0:
            rate = total_processed / elapsed_seconds
        else:
            rate = 0



        # Create progress bar
        bar_width = 30
        filled = int((percentage / 100) * bar_width)
        bar = '█' * filled + '░' * (bar_width - filled)

        # Color failed messages
        if self.failed_messages > 0:
            failed_section = f'{Style.RESET_ALL}{Fore.RED}Failed: {self.failed_messages:,}{Style.RESET_ALL}'
        else:
            failed_section = f'Failed: {self.failed_messages:,}'

        progress_line = (
            f'\r{Fore.GREEN}Progress: [{bar}] '
            f'{percentage:5.1f}% '
            f'({total_processed:,}/{self.total_messages:,}) '
            f'| Rate: {rate:6.1f} req/s '
            f'| Success: {self.completed_messages:,} '
            f'| {failed_section} |{Style.RESET_ALL}'
        )

        print(progress_line, end='', flush=True)

    def finish(self) -> 'None':
        """ Finish progress tracking.
        """
        end_time = utcnow()
        elapsed_time = end_time - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()

        total_processed = self.completed_messages + self.failed_messages
        average_rate = total_processed / elapsed_seconds if elapsed_seconds > 0 else 0

        print()  # New line after progress bar
        print(f'{Fore.CYAN}Completed: {self.completed_messages:,} messages in {elapsed_seconds:.2f}s{Style.RESET_ALL}')
        print(f'{Fore.CYAN}Average rate: {average_rate:.2f} req/s{Style.RESET_ALL}')
        if self.failed_messages > 0:
            print(f'{Fore.RED}Failed: {self.failed_messages:,} messages{Style.RESET_ALL}')

# ################################################################################################################################
