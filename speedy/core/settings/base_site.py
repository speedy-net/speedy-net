from .base_without_login import *
from .utils import update_site_paths
from speedy.net.settings.global_settings import * ########## ~~~~~ TODO


update_site_paths(settings=globals())

# We don't run tests on speedy.core
TEST_RUNNER = 'speedy.core.base.test.models.SpeedyCoreDiscoverRunner'


