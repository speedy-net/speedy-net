# -*- encoding: utf-8 -*-
"""
Django date and time format settings for the English language (en) in Speedy Core.
"""

# Django date format strings for the language 'en': DATE_FORMAT (full date) is "j F Y" and MONTH_DAY_FORMAT (month and day, without the year) is "j F".
DATE_FORMAT = "j F Y"
MONTH_DAY_FORMAT = "j F"


# Formats accepted as input for dates in the language 'en' (strptime format strings); only the ISO format YYYY-MM-DD is accepted.
DATE_INPUT_FORMATS = [
    "%Y-%m-%d",                           # '2006-10-25',
]


