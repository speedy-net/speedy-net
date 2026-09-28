from speedy.core.base.management.commands import makemessages


class Command(makemessages.Command):
    msgmerge_options = makemessages.Command.msgmerge_options + ["--no-fuzzy-matching"]


