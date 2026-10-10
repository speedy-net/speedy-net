from speedy.core.base.management.commands import makemessages


class Command(makemessages.Command):
    """
    A `make_messages` management command which extends the custom `makemessages` command, disabling fuzzy matching when merging message files.

    Attributes:
        msgmerge_options (list): The msgmerge options, with "--no-fuzzy-matching" appended.
    """
    msgmerge_options = makemessages.Command.msgmerge_options + ["--no-fuzzy-matching"]


