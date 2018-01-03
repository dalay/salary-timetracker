A handy tool with a command line interface for logging time worked. At any time you can see how much you have spent time on a particular project and how much you have earned on it.

## Features

- Track-file with data on time costs is created in the **root directory of the project's git repository**, which you are working on at the moment.
- Data is saved in [**CSV**](https://en.wikipedia.org/wiki/Comma-separated_values) format.

## Requirements and restrictions

- **Git**: The app will only work when you are inside a git repository.
- **Python 3**: The application was not tested to work under Python 2.

## Installation

```bash
pip install salary-timetracker
```
## Usage

```bash
tt [-h] [-s] {log} ...

positional arguments:
  {log}
    log          Create a new timetracker log record with time and
                 comments(optional)

optional arguments:
  -h, --help     show this help message and exit
  -s, --summary  Show summary.

```

```bash
tt log [-h] minutes [comments [comments ...]]

positional arguments:
  minutes     Time in minutes spent on work.
  comments    Commens on the work done (optional)

optional arguments:
  -h, --help  show this help message and exit
```

The app settings can be changed through the configuration file, which should be located along the path: ***~/.config/timetracker.conf***. And to have the following format:
```ini
[main]
# default settings
currency = 'USD'
hourly_rate = 20
default_comment = '' # comment when adding time
date_format = '%d %b %Y'
time_format = '%H:%M'
csv_delimiter =','
```

## Examples

Show help:
```bash
tt -h
```
You have worked for 2 hours and want to write this down:
```bash
tt log 120 'I did this'
# Data was successfully added
```
Show summary:
```bash
tt -s
# Hours worked: 2.6 | Salary: 52 USD
```
