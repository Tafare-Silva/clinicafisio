from .base import *

DEBUG = False

STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = "/var/www/clientes/fisioclin/staticfiles/"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = "/var/www/clientes/fisioclin/media/"

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    "http://159.65.167.110",
    "https://159.65.167.110",
    "http://fisioclin.blanjos.com.br",
    "https://fisioclin.blanjos.com.br",
]