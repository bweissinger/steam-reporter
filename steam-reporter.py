#!/usr/bin/env python3

import argparse
import imaplib
import keyring
import getpass
from config import Config
import concurrent.futures
import email_parser
import io
import tempfile
import sqlite3
import os

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

def _fetch_email(login_info, id):
    with _email_connection(*login_info) as connection:
        result, email = connection.fetch(id, '(RFC822)')
        return email

def _process_email(login_info, id):
    email = _fetch_email(login_info, id)
    with io.StringIO(email[0][1].decode("utf-8")) as email_file:
        return email_parser.parse_email_file(email_file)

def _post_transactions(transactions, database):
    if not os.path.exists(database):
        os.makedirs(os.path.dirname(database))

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        connection.execute('''CREATE TABLE IF NOT EXISTS steam_trades 
                (name text, amount real, date date, confirmation_number text UNIQUE)''')
        
        rows = connection.executemany('''INSERT OR IGNORE INTO steam_trades 
                (name, amount, date, confirmation_number) 
                VALUES (?, ?, ?, ?)''', 
                transactions)

        print(str(rows.rowcount) + ' transactions were added.')
        print(str(len(transactions) - rows.rowcount) + ' duplicate transactions were ignored.')

    return

def main():

    args = _parse_args()
    config = Config(args.config)

    if args.password: _set_keyring_password(config.keyring_id, config.email_address)

    login_info = [
        config.email_address,
        config.server_receive,
        config.keyring_id,
        config.email_folder
    ]

    ids = _get_steam_mail_ids(*login_info)

    transactions = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.processes) as executor:
        future_to_id = {executor.submit(_process_email, login_info, id): id for id in ids}
        for future in concurrent.futures.as_completed(future_to_id):
            if future.result() is not None:
                transactions.extend(future.result())
    _post_transactions(transactions, config.database)

    return

if __name__ == '__main__':
    main()