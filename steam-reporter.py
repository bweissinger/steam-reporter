#!/usr/bin/env python3

import argparse
import imaplib
import keyring
from config import Config

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

def email_connection(account, server, keyringID, folder):
    connection = imaplib.IMAP4_SSL(server)
    connection.login(account, keyring.get_password(keyringID, account))
    connection.select(folder)
    return connection

def main():
    args = _parse_args()
    config = Config(args.config)
    return

if __name__ == '__main__':
    main()