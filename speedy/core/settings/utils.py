import environ
from pathlib import Path

# Root directory of the project, the speedy.core app directory, and the environment variables reader (reads env.ini).
ROOT_DIR = Path(__file__).parent.parent.parent.parent
APP_DIR = ROOT_DIR / 'speedy' / 'core'
env = environ.Env()
environ.Env.read_env(str(ROOT_DIR / 'env.ini'))


def update_site_paths(settings):
    """
    Update the given settings dict in place with the per-app static, locale, templates and static files directories, based on the app's directory.

    :param settings: The settings dict to update. Must already contain an 'APP_DIR' key.
    :type settings: dict
    """
    app_dir = settings['APP_DIR']
    settings['STATIC_ROOT'] = str(app_dir / 'static_serve')
    settings['LOCALE_PATHS'].append(str(app_dir / 'locale'))
    settings['TEMPLATES'][0]['DIRS'].insert(0, str(app_dir / 'templates'))
    settings['STATICFILES_DIRS'].insert(0, str(app_dir / 'static'))


