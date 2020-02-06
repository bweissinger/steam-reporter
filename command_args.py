import argparse

def parse_args():
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
    parser.add_argument(
        '--update',
        '-u',
        action='store_true',
        help='Only add transactions after last date in database.'
    )
    parser.add_argument(
        '--mark_seen',
        '-m',
        action='store_true',
        help='Mark fetched emails as seen.'
    )

    return parser.parse_args()