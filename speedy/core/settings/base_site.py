from .base_without_login import *
from .utils import update_site_paths
from speedy.match.settings.global_settings import *  # ~~~~ TODO: Maybe we don't need this here? (added because the migrations fail).
from speedy.net.settings.global_settings import *  # ~~~~ TODO: Maybe we don't need this here? (added because the migrations fail).

update_site_paths(settings=globals())

SITE_ID = None

# We don't run tests on speedy.core
TEST_RUNNER = 'speedy.core.base.test.models.SpeedyCoreDiscoverRunner'


