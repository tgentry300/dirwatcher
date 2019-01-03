#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Directory watcher program, LRP"""

import time
import datetime
import logging
import signal
import argparse
import os

__author__ = "tgentry300"


logger = logging.getLogger(__file__)
exit_flag = False


def read_file_lines(file_to_read, starting_line, magic_text):
    """Reads files and logs if magic text is in line in file"""
    with open(file_to_read) as f:
        i = 0
        for i, line in enumerate(f, 1):
            if i >= starting_line:
                if magic_text in line:
                    logger.info('File: {} At line: {} Text: {}'
                                .format(file_to_read, i, line))
        return i


def sig_handler(sig_num, frame):
    """Handles signals passed from OS"""
    global exit_flag
    logger.warn('Received signal number {}'.format(str(sig_num)))

    if sig_num == signal.SIGINT or sig_num == signal.SIGTERM:
        exit_flag = True


def directory_watcher(directory_to_search, magic_text,
                      polling, filter_extension):
    """Watches directory for changes"""
    directory_to_search = os.path.abspath(directory_to_search)
    logger.info("I'm watching directory: {}".format(directory_to_search))

    tried_files = {}

    while not exit_flag:
        try:
            time.sleep(float(polling))
            file_list = []

            for f in os.listdir(directory_to_search):
                if f.endswith(filter_extension):
                    p = os.path.join(directory_to_search, f)
                    file_list.append(os.path.abspath(p))

            for file in file_list:
                if file not in tried_files:
                    logger.info('File added: {}'.format(file))
                    tried_files[file] = 1

            for file in list(tried_files):
                # Coerced tried_files into list for safe removal of items from
                # tried_files
                if file not in file_list:
                    logger.info('File removed: {}'.format(file))
                    del tried_files[file]

            for file, line_number in tried_files.items():
                tried_files[file] = read_file_lines(file, line_number,
                                                    magic_text) + 1

        except OSError as e:
            logger.warn(e)
            logger.info('Retrying in 5 seconds ...')
            time.sleep(5.0)
        except Exception as e:
            logger.error('Unhandled exception: {}'.format(e))
            logger.info('Retrying in 5 seconds ...')
            time.sleep(5.0)

    logger.warn('done with this program')


def main(directory_to_search, magic_text, polling, filter_extension):
    """Main function that sets up logger"""
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s'
               '%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)

    start_running_time = datetime.datetime.now()

    # Register sig handler with OS
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    # Startup Banner
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        '    Running {0}\n'
        '    Started on {1}\n'
        '-------------------------------------------------------------------\n'
        .format(__file__, start_running_time.isoformat())
    )

    directory_watcher(directory_to_search, magic_text,
                      polling, filter_extension)

    # Graceful DEATH of program
    uptime = datetime.datetime.now() - start_running_time
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        '   Stopped {}\n'
        '   Uptime was {}\n'
        '-------------------------------------------------------------------\n'
        .format(__file__, str(uptime)))


if __name__ == "__main__":
    """Sets up Parser and cmd line args, runs main"""
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Absolute path to directory to monitor')
    parser.add_argument('-m', '--magic',
                        help='Text to search in files in directory')
    parser.add_argument('-e', '--extension', help='Extension to filter on',
                        default='txt', type=str)
    parser.add_argument('-i', '--interval', help='Polling interval', default=1,
                        type=int)
    args = parser.parse_args()

    main(args.dir, args.magic, args.interval, args.extension)
