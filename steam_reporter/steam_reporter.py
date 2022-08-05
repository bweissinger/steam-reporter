#!/usr/bin/env python3
import steam_reporter.command_args
import steam_reporter.config
import steam_reporter.email_parser
import imaplib
import keyring
import getpass
import concurrent.futures
import io
import sqlite3
import os
import sys
import time

TIMEOUT_SECONDS = 30
TIMEOUT_TRIES = 10


def _email_connection(email_address, server, keyring_id, folder):
    connection = imaplib.IMAP4_SSL(server)

    for i in range(TIMEOUT_TRIES):
        try:
            connection.login(
                email_address, keyring.get_password(keyring_id, email_address)
            )
            connection.select(folder)
            if connection.state == "SELECTED":
                return connection
            else:
                raise ValueError("Failed to select folder '%s'\n" % folder)
        except (imaplib.IMAP4.error, ValueError) as error:
            print(
                "Failed to login to %s and select folder %s.\n"
                % (email_address, folder)
            )
            print("Error: %s\n" % error)
            time.sleep(TIMEOUT_SECONDS)

    sys.exit("Failed to connect.")


def _set_keyring_password(keyring_id, email_address):
    prompt = "Enter password for %s: " % email_address
    keyring.set_password(keyring_id, email_address, getpass.getpass(prompt))


def _get_steam_mail_ids(email_address, server, keyring_id, folder, date):
    with _email_connection(email_address, server, keyring_id, folder) as connection:
        if date:
            date = '(SINCE "' + date.strftime("%d-%b-%Y") + '")'
        result, message_ids = connection.search(None, '(FROM "Steam Store")', date)
        return message_ids[0].split()


def _fetch_email(login_info, id, mark_seen):
    message_parts = "(RFC822)" if mark_seen else "(BODY.PEEK[])"
    with _email_connection(*login_info) as connection:
        result, email = connection.fetch(id, message_parts)
        return email


def _process_email(login_info, id, mark_seen):
    email = _fetch_email(login_info, id, mark_seen)
    with io.StringIO(email[0][1].decode("utf-8")) as email_file:
        return steam_reporter.email_parser.parse_email_file(email_file)


def _process_local_file(id):
    with open(id, "r") as email:
        return steam_reporter.email_parser.parse_email_file(email)


def _post_transactions(transactions, database):
    with sqlite3.connect(
        database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    ) as connection:
        rows = connection.executemany(
            """INSERT OR IGNORE INTO steam_trades
                (name, amount, date, confirmation_number)
                VALUES (?, ?, ?, ?)""",
            transactions,
        )

        print(str(rows.rowcount) + " transactions were added.")
        print(
            str(len(transactions) - rows.rowcount)
            + " duplicate transactions were ignored."
        )

    return


def _get_last_transaction_date(database):
    with sqlite3.connect(
        database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    ) as connection:

        cursor = connection.cursor()
        cursor.execute("""SELECT date FROM steam_trades ORDER BY date DESC LIMIT 1""")
        date = cursor.fetchone()

        return date[0] if date else None

    return None


def _create_database_if_not_exists(database):
    if not os.path.exists(database):
        os.makedirs(os.path.dirname(database), exist_ok=True)

        with sqlite3.connect(
            database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        ) as connection:
            connection.execute(
                """CREATE TABLE steam_trades"""
                """ (name text, amount int, date timestamp, confirmation_number text UNIQUE)"""
            )


def _get_ids(config, login_info, date):
    if config.local_folder:
        return [
            os.path.join(config.local_folder, filename)
            for filename in os.listdir(config.local_folder)
        ]
    return _get_steam_mail_ids(*login_info, date)


def _threaded_parsing(num_threads, local_folder, ids, login_info, mark_seen):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        if local_folder:
            future_to_id = {executor.submit(_process_local_file, id): id for id in ids}
        else:
            future_to_id = {
                executor.submit(_process_email, login_info, id, mark_seen): id
                for id in ids
            }

        transactions = []
        for future in concurrent.futures.as_completed(future_to_id):
            if future.result() is not None:
                transactions.extend(future.result())
        return transactions


def main():

    args = steam_reporter.command_args.parse_args()
    config = steam_reporter.config.Config(args.config)

    _create_database_if_not_exists(config.database)

    if args.password:
        _set_keyring_password(config.keyring_id, config.email_address)

    login_info = [
        config.email_address,
        config.email_server,
        config.keyring_id,
        config.email_folder,
    ]

    date = None if not args.update else _get_last_transaction_date(config.database)

    ids = _get_ids(config, login_info, date)

    while ids:
        if config.emails_per_transaction <= 0:
            ids_for_transaction = ids
            ids = []
        else:
            ids_for_transaction = ids[: config.emails_per_transaction]
            ids = ids[config.emails_per_transaction + 1 :]

        transactions = _threaded_parsing(
            config.threads,
            config.local_folder,
            ids_for_transaction,
            login_info,
            args.mark_seen,
        )
        _post_transactions(transactions, config.database)

    return


if __name__ == "__main__":
    main()
