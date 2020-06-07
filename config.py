from dataclasses import dataclass
import configparser

@dataclass(frozen=True)
class Config:
    """ConfigParser wrapper"""

    email_folder: str
    threads: int
    database: str
    email_address: str
    server_receive: str
    server_send: str
    local_folder: str
    keyring_id: str = 'steam-reporter'
    emails_per_transaction: int = 0

    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        
        try:
            object.__setattr__(self, 'email_folder', config.get('General', 'Email_Folder'))
        except configparser.NoOptionError:
            object.__setattr__(self, 'email_folder', 'INBOX')
        try:
            object.__setattr__(self, 'local_folder', config.get('General', 'Local_Folder'))
        except configparser.NoOptionError:
            object.__setattr__(self, 'local_folder', None)


        object.__setattr__(self, 'threads', config.getint('General', 'Threads'))
        object.__setattr__(self, 'database', config.get('General', 'Database'))
        object.__setattr__(self, 'email_address', config.get('General', 'Email_Address'))
        object.__setattr__(self, 'server_receive', config.get('Receive', 'Server'))
        object.__setattr__(self, 'server_send', config.get('Send', 'Server'))
        object.__setattr__(self, 'emails_per_transaction', config.getint('General', 'Emails_Per_Transaction', ))