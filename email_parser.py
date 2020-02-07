import collections
import re
from datetime import datetime

SUBJECT_SELL = "Subject: You have sold an item on the Community Market"
SUBJECT_PURCHASE = "Subject: Thank you for your Community Market purchase"

Transaction = collections.namedtuple('Transaction', 'title amount date number')

def parse_transactions(email, purchase=True):
    transactions = []
    seek_to_line(email, "https://store.steampowered.com/account")

    endOfTransactionsDelimiter="------"
    if not purchase:
        endOfTransactionsDelimiter="Total"

    names, amounts = [], []
    for transaction in remove_none_elements(get_lines_until(email, endOfTransactionsDelimiter)):
        name, amount = split_name_and_amount(transaction)
        names.append(name)
        if purchase: amount = 0 - amount
        amounts.append(amount)

    confirmationNumbers = get_confirmation_numbers(email)
    date = get_date(email)

    for name,amount,confirmationNumber in zip(names,amounts, confirmationNumbers):
        transactions.append(Transaction(
            title=name,
            amount=amount, 
            date=date, 
            number=confirmationNumber))

    return transactions
    
def get_confirmation_numbers(email):
    for line in email:
        if line == "":
            return None
        if "Confirmation Number" in line:
            confirmationNumbers = remove_none_elements(line.rstrip().split(" "))[2:]
            return remove_commas(confirmationNumbers)

def get_date(email):
    for line in email:
        if line == "":
            return None
        if "Date Confirmed" in line:
            fullDate = line.rstrip().split(" ", 3)[3]
            return datetime.strptime(''.join(fullDate).strip(), "%a %b %d %H:%M:%S %Y")

def split_name_and_amount(string):
    name, amount = re.split("(:\s+\d+\D+\d+)", string)[:2]
    amount = amount.replace(": ", "")
    amount = int(amount.replace(".", ""))
    return name, amount

def remove_usd(string):
    return string.split(" ", 1)[0]

def remove_commas(strings):
    return [element.replace(',', '') for element in strings]

def remove_none_elements(strings):
    return list(filter(None, strings))

def get_lines_until(email, string):
    lines=[]
    for line in email:
        if string == "":
            break
        if string not in line.rstrip():
            lines.append(line.rstrip())
        else:
            break
    return lines

def seek_to_line(email, string):
    for line in email:
        if string == "":
            return
        if string in line:
            return

def has_subject_line(email, subject):
    """Determine if email has specific subject line"""

    email.seek(0)
    for line in email:
        if subject in line:
            return True
    return False

def parse_email_file(opened_email_file):
    """Takes in an opened file, returns parsed transactions."""

    if has_subject_line(opened_email_file, SUBJECT_PURCHASE):
        return parse_transactions(opened_email_file)
    elif has_subject_line(opened_email_file, SUBJECT_SELL):
        return parse_transactions(opened_email_file, purchase=False)

    return None