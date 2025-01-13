from django.core.management.commands import test


class Command(test.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser=parser)

        group = parser.add_argument_group('language options', 'These arguments are mutually exclusive. Default: --test-default-languages')
        language_group = group.add_mutually_exclusive_group()
        language_group.add_argument(
            "--test-all-languages",
            action="store_const",
            const="test-all-languages",
            dest="test_languages",
            help="Run tests for all languages, and don't skip languages.",
        )
        language_group.add_argument(
            "--test-default-languages",
            action="store_const",
            const="test-default-languages",
            dest="test_languages",
            help="Run tests for default languages (English, French, Hebrew + randomly select one more language or none).",
        )
        language_group.add_argument(
            "--test-only-english",
            action="store_const",
            const="en",
            dest="test_languages",
            help="Run tests for only English.",
        )
        language_group.add_argument(
            "--test-only-language-code",
            action="store",
            dest="test_languages",
            help="Run tests for only one language (the given language code).",
            type=str,
        )
        parser.set_defaults(test_languages="test-default-languages")
        # Running tests with --test-only-language-code en is equivalent to running tests with --test-only-english.

        parser.add_argument(
            "--test-only",
            action="store",
            help="If run with this argument, run only this number of tests.",
            type=int,
        )

        parser.add_argument(
            "--count-tests",
            action="store",
            help="If run with this argument, count the tests grouped by name of this depth. If passed without a number, defaults to 3.",
            type=int,
            nargs="?",
            const=3,
        )


