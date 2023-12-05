from django.core.management.commands import makemessages


class Command(makemessages.Command):
    msgmerge_options = makemessages.Command.msgmerge_options + ["--no-fuzzy-matching"]

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--no-fuzzy-matching',
            action='store_true',
            help='Do not use fuzzy matching in msgmerge.',
        )


