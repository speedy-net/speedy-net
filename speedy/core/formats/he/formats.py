# -*- encoding: utf-8 -*-

# Django date format strings for the language 'he': DATE_FORMAT (full date) is "j בF Y" and MONTH_DAY_FORMAT (month and day, without the year) is "j בF".
DATE_FORMAT = "j בF Y"
MONTH_DAY_FORMAT = "j בF"


# Formats accepted as input for dates in the language 'he' (strptime format strings); only the ISO format YYYY-MM-DD is accepted.
DATE_INPUT_FORMATS = [
    "%Y-%m-%d",                           # '2006-10-25',
]


