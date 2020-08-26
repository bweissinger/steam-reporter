Creates a mysql database of your steam market transactions through the parsing of steam emails.


# Installation

## Setup of config file
You must create a config file with your specific email settings. You can copy the default config to your preferred location.

```cp steam_reporter/config/config.ini /your/preferred/location/```

## Configuration

### Threads

`Threads = 5`

Steam-reporter is multi-threaded to speed up the fetching of emails from email servers. Note that it will have little impact on the actuall parsing of emails, and multiple threads probably isn't needed if you are using local .eml files.

### Emails_Per_Transaction

`Emails_Per_Transaction = 1000`

This limits the number of emails parsed before performing the transaction with the database. Note that each email can have multiple steam market confirmations, so the number of steam transactions added per each database transaction can be greater than the number set.
This setting can be useful for low memory situations, or to provide more frequent status updates during processing.

### Database

`Database = /home/user/example/database.db`

The location of the database. A new database will be created if one does not exist at the provided path.

### Local_Folder

`Local_Folder = /home/user/example/downloaded_emails/`

This is an optional configuration to allow you to use local email files instead of fetching them from the server. If you do not want to use this option, leave it commented out.

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
