#!/usr/bin/env python3

import argparse
import imaplib
import keyring
import getpass
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
    parser.add_argument(
        '--password',
        '-p',
        action='store_true',
        help='Set password in keyring.'
    )

    return parser.parse_args()

def email_connection(account, server, keyring_id, folder):
    connection = imaplib.IMAP4_SSL(server)
    connection.login(account, keyring.get_password(keyring_id, account))
    connection.select(folder)
    return connection

def set_keyring_password(keyring_id, email_address):
    prompt = ("Enter password for %s: " % email_address)
    keyring.set_password(
        keyring_id, 
        email_address, 
        getpass.getpass(prompt))

def main():

    args = _parse_args()
    config = Config(args.config)

    if args.password: set_keyring_password(config.keyring_id, config.email_address)

    return

if __name__ == '__main__':
    main()