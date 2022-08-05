from dataclasses import dataclass
import configparser


@dataclass(frozen=True)
class Config:
    """ConfigParser wrapper"""

    email_folder: str
    threads: int
    database: str
    email_address: str
    email_server: str
    local_folder: str
    emails_per_transaction: int
    keyring_id: str = "steam-reporter"

    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)

        try:
            object.__setattr__(self, "email_folder", config.get("Email", "Folder"))
        except configparser.NoOptionError:
            object.__setattr__(self, "email_folder", "INBOX")
        try:
            object.__setattr__(
                self, "local_folder", config.get("General", "Local_Folder")
            )
        except configparser.NoOptionError:
            object.__setattr__(self, "local_folder", None)

        object.__setattr__(self, "threads", config.getint("General", "Threads"))
        object.__setattr__(self, "database", config.get("General", "Database"))
        object.__setattr__(self, "email_address", config.get("Email", "Address"))
        object.__setattr__(self, "email_server", config.get("Email", "Server"))
        object.__setattr__(
            self,
            "emails_per_transaction",
            config.getint(
                "General",
                "Emails_Per_Transaction",
            ),
        )
