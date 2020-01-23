from dataclasses import dataclass
import configparser

@dataclass(frozen=True)
class Config:
    """ConfigParser wrapper"""

    email_folder: str
    processes: int
    database: str
    server_receive: str
    server_send: str
    keyring_id: str = 'steam-reporter'

    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        
        try:
            object.__setattr__(self, 'email_folder', config.get('General', 'Email_Folder'))
        except configparser.NoOptionError:
            object.__setattr__(self, 'email_folder', 'All')
            pass

        object.__setattr__(self, 'processes', config.get('General', 'Processes'))
        object.__setattr__(self, 'database', config.get('General', 'Database'))
        object.__setattr__(self, 'server_receive', config.get('Receive', 'Server'))
        object.__setattr__(self, 'server_send', config.get('Send', 'Server'))