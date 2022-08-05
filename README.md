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

`Threads = 1`

This is the number of processes to use. It is unlikely to have much impact unless you are processing very large numbers of local files. steam-reporter was moved to multiprocessing, but `Threads` was kept to remain compatibility for people with existing configs


### Emails_Per_Transaction

`Emails_Per_Transaction = 1000`

Rows_Per_Transaction : Number of files/emails to process at one time. Due to the possibility of multiple transaction included in each email, the actual number of commited transactions may be more. Has most impact on emails, not local files. Larger numbers increase memory usage. NOTE :::: There appears to be a limit to the number of characters supplied to the IMAP fetch command. If this occurs (a FETCH command error, or unterminated line) reduce this number. As id lengths increase (i.e. 200 vs 2000 vs 20000) this number may have to be reduced.


### Database

`Database = /home/user/example/database.db`

Location of database to use. A new database will be created if it does not exist.

### Local_Folder

`Local_Folder = /home/user/example/downloaded_emails/`

Uncomment this line to use local eml files instead of fetching from server.

`# Local_Folder = `

### Address

`Address = example@email.com`

Email address to fetch emails from.

### Server

`Server = imap.email.com`

Email server for the address.

### Folder

`Folder = Steam_Emails_Location`

Uncomment this line to search a specific inbox folder. Use this if your steam market transaction emails are not located in your main inbox folder.

`# Folder = `

## Troubleshooting
### Failing to Login/App Specific Passwords
Some email providers, such as hotmail, now require an app specific password in order for third party applications to login. If steam-reporter fails to connect to your email account, this may be why. There should be an option in your email account settings to generate an app specific password. Use this in place of your regular password

### FETCH Error
When fetching emails from the server, the fetch command can take a series of ids - such as `1:4`, `1,2,3,4`, or `1,3:5`. There appears to be a limit to the length of the command that can be sent. If you get an error regarding a FETCH command error, you probably need to reduce the emails per transaction in your config file.
