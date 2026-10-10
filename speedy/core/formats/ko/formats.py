# -*- encoding: utf-8 -*-
"""
Django date and time format settings for the Korean language (ko) in Speedy Core.
"""

# Django date format strings for the language 'ko': DATE_FORMAT (full date) is "Y년 n월 j일" and MONTH_DAY_FORMAT (month and day, without the year) is "n월 j일".
DATE_FORMAT = "Y년 n월 j일"
MONTH_DAY_FORMAT = "n월 j일"


# Formats accepted as input for dates in the language 'ko' (strptime format strings); only the ISO format YYYY-MM-DD is accepted.
DATE_INPUT_FORMATS = [
    "%Y-%m-%d",                           # '2006-10-25',
]


