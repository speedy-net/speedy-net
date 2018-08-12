import environ
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.parent
APP_DIR = ROOT_DIR / 'speedy' / 'core'
env = environ.Env()
environ.Env.read_env(str(ROOT_DIR / 'env.ini'))
