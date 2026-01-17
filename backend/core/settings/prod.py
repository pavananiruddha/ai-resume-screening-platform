from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Production tweaks (Example: Secure cookies, S3 storage, etc)
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
