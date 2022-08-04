# steam-reporter
`steam-reporter` is a command line tool that parses steam markent email receipts and stores transaction information in a local SQLite database. It is currently only tested and configured for US based users.

## Installation
`pip install steam_reporter`

## Setup
### config.ini
Copy the repos [default config file](https://github.com/bweissinger/steam-reporter/blob/master/steam_reporter/config/config.ini) to a directory of your choice, such as `~/path_to_config/config.ini`. Complete the `database`, `address`, and `server` sections according to your use case. See below for an overview of each section in the config file. If you have multiple email accounts you need to fetch transactions from, create a config.ini file for each email address, and run `steam-reporter` for each config file. They can point to the same database file if needed.

### keyring
`steam-reporter` uses the python keyring library to securely handle email account credentials. Credentials must be added before use. `steam-reporter` can be used as a frontend for setting keyring credentials via the `-p` flag. For example, `steam_reporter -p config_file_path/config.ini`. You will then be prompted for username and password. If you would like to set the credentials manually, use the service name `steam-reporter`.

## Usage

It's as simple as 
```
$ steam_reporter /config_file_path/config.ini
```

### Syntax
`steam_reporter [-h] [--quiet] [--password] [--update] [--mark_seen] config`

### Positional Arguments
`config` - the location of the intended config file, such as `~/path_to_config/config.ini`

### Options
`-h`, `--help` - Shows help.
\
`-q`, `--quiet` - Prevents printing to console.
\
`-p`, `--password` - Sets the username and password in the local keyring.
\
`-u`, `--update` - Only adds transactions on and after the last dated transaction in the database.
\
`-m`, `--mark_seen` - Marks fetched emails as seen.


## Config File Options

### Threads

`Threads = 5`

`steam-reporter` is multi-threaded, and the number of threads can be set with this option.

### Emails_Per_Transaction

`Emails_Per_Transaction = 1000`

This limits the number of emails parsed before performing the transaction with the database. Note that each email can have multiple steam market confirmations, so the number of steam transactions added per each database transaction can be different than the number set.
This setting can be useful for low memory situations, or to provide more frequent status updates during processing.

### Database

`Database = /home/user/example/database.db`

The location of the database. A new database will be created if one does not exist at the provided path. Multiple configs can point to the same database.

### Local_Folder

`Local_Folder = /home/user/example/downloaded_emails/`

This is an optional configuration to allow you to use email files stored locally instead of fetching them from the server. If you do not want to use this option, leave it commented out.

`# Local_Folder = `

### Address

`Address = example@email.com`

The email address that your steam market confirmation emails are sent to.

### Server

`Server = imap.email.com`

This is the server address for the provided email address.

### Folder

`Folder = Steam_Emails_Location`

If you route your steam emails to a specific folder within your inbox, make sure to uncomment this line and add the name of the folder. If they are located in your main inbox, leave it commented out.

`# Folder = `
