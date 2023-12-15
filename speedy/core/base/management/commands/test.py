from django.core.management.commands import test


class Command(test.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser=parser)
        parser.add_argument(
            "--test-all-languages",
            action="store_true",
            help="If run with this argument, test all languages, and don't skip languages.",
        )


