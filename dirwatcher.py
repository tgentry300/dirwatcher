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


def read_file_lines(file_to_read):
    with open(file_to_read) as f:
        return f.readlines()


def sig_handler(sig_num, frame):
    """Handles signals passed from OS"""
    global exit_flag
    logger.warn('Received signal number {}'.format(str(sig_num)))

    if sig_num == signal.SIGINT or sig_num == signal.SIGTERM:
        exit_flag = True


def directory_watcher(directory_to_search, magic_text,
                      polling, filter_extension):
    """Watches directory for changes"""
    logger.info('Running this directory watcher function')
    tried_files = []

    while not exit_flag:
        try:
            time.sleep(float(polling))
            os.chdir(directory_to_search)
            directory = os.listdir(directory_to_search)
            for file in directory:
                print file
                if file not in tried_files:
                    tried_files.append(file)
                    file_lines = read_file_lines(file)
                else:
                    break
                for i, line in enumerate(file_lines):
                    if magic_text in line:
                        logger.info('File: {} At line: {} Text: {}'
                                    .format(file, i + 1, line))

        except OSError as e:
            logger.warn("this is an OS Error")
        except Exception as e:
            # Something bad has happened
            logger.error('Unhandled exception: {}'.format(e))
            logger.info('Retrying in 5 seconds ...')
            time.sleep(5.0)

    logger.warn('done with this program')


def main(directory_to_search, magic_text, polling, filter_extension):
    """Main function that sets up logger"""
    logging.basicConfig(
        filename='log.txt',
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
    parser.add_argument('-dir', help='Absolute path to directory to monitor')
    parser.add_argument('-magic', help='Text to search in files in directory')
    parser.add_argument('-ext', help='Extension to filter on')
    parser.add_argument('--int', help='Polling interval')
    args = parser.parse_args()

    directory_to_search = args.dir
    magic_text = args.magic

    if args.int:
        polling = args.int
    else:
        polling = 1

    if args.ext:
        filter_extension = args.ext

    main(directory_to_search, magic_text, polling, filter_extension)
