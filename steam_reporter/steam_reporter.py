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


def _get_ids(config, date):
    if config.local_folder:
        return [
            os.path.join(config.local_folder, filename)
            for filename in os.listdir(config.local_folder)
        ]
    else:
        with _email_connection(
            config.email_address,
            config.email_server,
            config.keyring_id,
            config.email_folder,
        ) as connection:
            if date:
                date = '(SINCE "' + date.strftime("%d-%b-%Y") + '")'
            result, message_ids = connection.search(None, '(FROM "Steam Store")', date)
            return message_ids[0].split()


def _process_email(email):
    with io.StringIO(email[1].decode("utf-8")) as email_file:
        return steam_reporter.email_parser.parse_email_file(email_file)


def _process_local_file(id):
    with open(id, "r") as email:
        return steam_reporter.email_parser.parse_email_file(email)


def _threaded_parsing(config, ids, mark_seen):
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.threads) as executor:
        if config.local_folder:
            future_to_id = {executor.submit(_process_local_file, id): id for id in ids}
        else:
            message_parts = "(RFC822)" if mark_seen else "(BODY.PEEK[])"
            with _email_connection(
                config.email_address,
                config.email_server,
                config.keyring_id,
                config.email_folder,
            ) as connection:
                result, emails = connection.fetch(b",".join(ids), message_parts)
            future_to_id = {
                executor.submit(_process_email, email): email
                for email in emails
                if len(email) == 2
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

    date = None if not args.update else _get_last_transaction_date(config.database)

    ids = _get_ids(config, date)

    while ids:
        if config.emails_per_transaction <= 0:
            ids_for_transaction = ids
            ids = []
        else:
            ids_for_transaction = ids[: config.emails_per_transaction]
            ids = ids[config.emails_per_transaction + 1 :]

        transactions = _threaded_parsing(
            config,
            ids_for_transaction,
            args.mark_seen,
        )
        _post_transactions(transactions, config.database)

    return


if __name__ == "__main__":
    main()
