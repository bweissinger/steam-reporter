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

def _email_connection(email_address, server, keyring_id, folder):
    connection = imaplib.IMAP4_SSL(server)

    try:
        connection.login(email_address, keyring.get_password(keyring_id, email_address))
    except:
        print("\nFailed to login to %s. Make sure you have set the correct keyring "
            "password with the -p/--password flag.\n" % email_address)
        raise

    connection.select(folder)
    return connection

def _set_keyring_password(keyring_id, email_address):
    prompt = ("Enter password for %s: " % email_address)
    keyring.set_password(
        keyring_id, 
        email_address, 
        getpass.getpass(prompt))

def _get_steam_mail_ids(email_address, server, keyring_id, folder):
    with _email_connection(email_address, server, keyring_id, folder) as connection:
        result, message_ids = connection.search(None, "ALL")
        return message_ids[0].split()

def _fetch_email(connection, id):
    result, email = connection.fetch(id, '(RFC822)')
    return email

def main():

    args = _parse_args()
    config = Config(args.config)

    if args.password: _set_keyring_password(config.keyring_id, config.email_address)

    return

if __name__ == '__main__':
    main()