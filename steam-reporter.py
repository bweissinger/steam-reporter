#!/usr/bin/env python3

import imaplib
import keyring
import getpass
from config import Config
from datetime import datetime
import concurrent.futures
import email_parser
import io
import tempfile
import sqlite3
import os
import command_args

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

def _get_steam_mail_ids(email_address, server, keyring_id, folder, date):
    with _email_connection(email_address, server, keyring_id, folder) as connection:
        if date:
            date = '(SINCE "' + date.strftime("%d-%b-%Y") + '")'
        result, message_ids = connection.search(None, '(FROM "Steam Store")', date)
        return message_ids[0].split()

def _fetch_email(login_info, id, mark_seen):
    message_parts = '(RFC822)' if mark_seen else '(BODY.PEEK[])'
    with _email_connection(*login_info) as connection:
        result, email = connection.fetch(id, message_parts)
        return email

def _process_email(login_info, id, mark_seen):
    email = _fetch_email(login_info, id, mark_seen)
    with io.StringIO(email[0][1].decode("utf-8")) as email_file:
        return email_parser.parse_email_file(email_file)

def _post_transactions(transactions, database):
    with sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as connection:        
        rows = connection.executemany('''INSERT OR IGNORE INTO steam_trades 
                (name, amount, date, confirmation_number) 
                VALUES (?, ?, ?, ?)''', 
                transactions)

        print(str(rows.rowcount) + ' transactions were added.')
        print(str(len(transactions) - rows.rowcount) + ' duplicate transactions were ignored.')

    return

def _get_last_transaction_date(database):
    with sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as connection:

        cursor = connection.cursor()
        cursor.execute('''SELECT date FROM steam_trades ORDER BY date DESC LIMIT 1''')
        date = cursor.fetchone()

        return date[0] if date else None

    return None

def _create_database_if_not_exists(database):
    if not os.path.exists(database):
        os.makedirs(os.path.dirname(database), exist_ok=True)

        with sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as connection:
            cursor = connection.cursor()

            connection.execute('''CREATE TABLE steam_trades 
                    (name text, amount real, date timestamp, confirmation_number text UNIQUE)''')

def main():

    args = command_args.parse_args()
    config = Config(args.config)

    _create_database_if_not_exists(config.database)

    if args.password: _set_keyring_password(config.keyring_id, config.email_address)

    login_info = [
        config.email_address,
        config.server_receive,
        config.keyring_id,
        config.email_folder
    ]

    date = None if not args.update else _get_last_transaction_date(config.database)

    ids = _get_steam_mail_ids(*login_info, date)

    while ids:
        if config.emails_per_transaction <= 0:
            ids_for_transaction = ids
            ids = []
        else:
            ids_for_transaction = ids[:config.emails_per_transaction]
            ids = ids[(config.emails_per_transaction + 1):]

        transactions = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.processes) as executor:
            future_to_id = {executor.submit(_process_email, login_info, id, args.mark_seen): id for id in ids_for_transaction}
            for future in concurrent.futures.as_completed(future_to_id):
                if future.result() is not None:
                    transactions.extend(future.result())
        _post_transactions(transactions, config.database)

    return

if __name__ == '__main__':
    main()