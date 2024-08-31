# Certs Reminder
## Description
This program loads a CSV file exported from FortiClient Endpoint Management Server (Forti EMS), parses it,
calculates the date difference and sends an email with information about which certificates have expired
and will expire within specified days.

### History
I wrote this program in 2022 for my friends.

## Installation
Clone this repository or download the source code in .zip archive.

## Usage
Rename `.env.dist` file to `.env` and fill in the details of the sender mailbox and receiver address.\
They will be used as environment variables.