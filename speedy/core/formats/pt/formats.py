# -*- encoding: utf-8 -*-

# Django date format strings for the language 'pt': DATE_FORMAT (full date) is r"j \d\e F \d\e Y" and MONTH_DAY_FORMAT (month and day, without the year) is r"j \d\e F".
DATE_FORMAT = r"j \d\e F \d\e Y"
MONTH_DAY_FORMAT = r"j \d\e F"


# Formats accepted as input for dates in the language 'pt' (strptime format strings); only the ISO format YYYY-MM-DD is accepted.
DATE_INPUT_FORMATS = [
    "%Y-%m-%d",                           # '2006-10-25',
]


