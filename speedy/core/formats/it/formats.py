# -*- encoding: utf-8 -*-
"""
Django date and time format settings for the Italian language (it) in Speedy Core.
"""

# Django date format strings for the language 'it': DATE_FORMAT (full date) is "d F Y" and MONTH_DAY_FORMAT (month and day, without the year) is "j F".
DATE_FORMAT = "d F Y"
MONTH_DAY_FORMAT = "j F"


# Formats accepted as input for dates in the language 'it' (strptime format strings); only the ISO format YYYY-MM-DD is accepted.
DATE_INPUT_FORMATS = [
    "%Y-%m-%d",                           # '2006-10-25',
]


