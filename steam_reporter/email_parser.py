import collections
import re
from datetime import datetime
from dateutil import parser

SUBJECT_SELL = "Subject: You have sold an item on the Community Market"
SUBJECT_PURCHASE = "Subject: Thank you for your Community Market purchase"

Transaction = collections.namedtuple("Transaction", "title amount date number")


def _parse_transactions(email, purchase=True):
    transactions = []
    _seek_to_line(email, "https://store.steampowered.com/account")

    endOfTransactionsDelimiter = "------"
    if not purchase:
        endOfTransactionsDelimiter = "Total"

    names, amounts = [], []
    for transaction in _remove_none_elements(
        _get_lines_until(email, endOfTransactionsDelimiter)
    ):
        name, amount = _split_name_and_amount(transaction)
        names.append(name)
        if purchase:
            amount = 0 - amount
        amounts.append(amount)

    confirmationNumbers = _get_confirmation_numbers(email)
    date = _get_date(email)

    if len(confirmationNumbers) != len(names):
        names, amounts = _parse_multiple_copies(
            names, amounts, len(confirmationNumbers), date
        )
        if not names or not amounts:
            return []

    for name, amount, confirmationNumber in zip(names, amounts, confirmationNumbers):
        transactions.append(
            Transaction(title=name, amount=amount, date=date, number=confirmationNumber)
        )

    return transactions


def _parse_multiple_copies(names, amounts, correct_num_transactions, date):
    num_copies = []
    corrected_names = []
    for name in names:
        num, corrected_name = _parse_num_copies_and_correct_name(name)
        corrected_names.append(corrected_name)
        num_copies.append(num)

    if correct_num_transactions != sum(num_copies):
        try:
            print(
                "Unable to successfully parse email from "
                + date.strftime("%Y-%m-%d %H:%M:%S")
                + " with transactions: "
                + " ".join(names)
            )
        except:
            print("Unable to successfully parse email")
        return [], []

    tmp_names = []
    tmp_amounts = []
    for name, num, amount in zip(corrected_names, num_copies, amounts):
        tmp_names.extend([name] * num)
        tmp_amounts.extend([amount] * num)

    return tmp_names, tmp_amounts


def _parse_num_copies_and_correct_name(name):
    try:
        match = re.match("(^\d+\s+)", name).group(0)
        num_copies = match.replace(" ", "")
        name = name.replace(match, "")
        return int(num_copies), name
    except:
        return 1, name


def _get_confirmation_numbers(email):
    line = _seek_to_line(email, "Confirmation Number")
    try:
        confirmationNumbers = _remove_none_elements(line.rstrip().split(" "))[2:]
        if len(confirmationNumbers) == 0:
            raise Exception
        return _remove_commas(confirmationNumbers)
    except Exception:
        pass
    # Confirmation numbers may be on next line of Buy confirmation emails
    try:
        return _remove_none_elements(next(email).rstrip().split())
    except Exception:
        return None


def _get_date(email):
    line = _seek_to_line(email, "Date Confirmed")
    try:
        return parser.parse(line, fuzzy=True)
    except Exception:
        pass
    # Date may be on next line of Buy confirmation emails
    try:
        return parser.parse(next(email), fuzzy=True)
    except Exception:
        return None


def _split_name_and_amount(string):
    name, amount = re.split("(:\s+\d+\D+\d+)", string)[:2]
    amount = amount.replace(": ", "")
    amount = int(amount.replace(".", ""))
    return name, amount


def _remove_commas(strings):
    return [element.replace(",", "") for element in strings]


def _remove_none_elements(strings):
    return list(filter(None, strings))


def _get_lines_until(email, string):
    lines = []
    for line in email:
        if string == "":
            break
        if string not in line.rstrip():
            lines.append(line.rstrip())
        else:
            break
    return lines


def _seek_to_line(email, string):
    for line in email:
        if string == "" or string in line:
            return line


def _has_subject_line(email, subject):
    """Determine if email has specific subject line"""

    email.seek(0)
    for line in email:
        if subject in line:
            return True
    return False


def parse_email_file(opened_email_file):
    """Takes in an opened file, returns parsed transactions."""

    if _has_subject_line(opened_email_file, SUBJECT_PURCHASE):
        return _parse_transactions(opened_email_file)
    elif _has_subject_line(opened_email_file, SUBJECT_SELL):
        return _parse_transactions(opened_email_file, purchase=False)

    return []
