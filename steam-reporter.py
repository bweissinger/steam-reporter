#!/usr/bin/env python3

import argparse

def _parse_args():
    """Use argparse to get args from command line"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config',
        help='Config file')
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='do not print to console'
    )

    return parser.parse_args()

def main():
    args = _parse_args()
    return

if __name__ == '__main__':
    main()