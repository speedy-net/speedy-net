from django.core.management.commands.makemessages import Command as MakeMessagesCommand


class Command(MakeMessagesCommand):
    msgmerge_options = ['-q', '--previous', '--no-fuzzy-matching']


