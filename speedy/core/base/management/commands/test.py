from django.core.management.commands import test


class Command(test.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser=parser)

        group = parser.add_argument_group('language options', 'These arguments are mutually exclusive. Default: --test-default-languages')
        language_group = group.add_mutually_exclusive_group()
        language_group.add_argument(
            "--test-all-languages",
            action="store_true",
            help="Run tests for all languages, and don't skip languages.",
        )
        language_group.add_argument(
            "--test-default-languages",
            action="store_true",
            help="Run tests for default languages (English, French, Hebrew + randomly select one more language or none).",
        )
        language_group.add_argument(
            "--test-only-english",
            action="store_true",
            help="Run tests for only English.",
        )
        language_group.add_argument(
            "--test-only-language-code",
            action="store",
            help="Run tests for only one language (the given language code).",
            type=str,
        )
        # Running tests with --test-only-language-code en is equivalent to running tests with --test-only-english.

        parser.add_argument(
            "--test-only",
            action="store",
            help="If run with this argument, run only this number of tests.",
            type=int,
        )


