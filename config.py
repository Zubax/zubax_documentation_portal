import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = bool(os.environ.get('FLASK_DEBUG', False))
if DEBUG:
    print('WARNING DEBUG ENABLED')

# A common general assumption is using 2 per available processor cores - to handle
# incoming requests using one and performing background operations using the other.
THREADS_PER_PAGE = 2

#
# Security
#
CSRF_ENABLED     = True
CSRF_SESSION_KEY = os.environ['SESSION_SECRET']

SECRET_KEY = os.environ['SESSION_SECRET']
