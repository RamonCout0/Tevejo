from django.contrib.messages import constants as messages
from pathlib import Path
import os

# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# Security
# ============================================================

# Usar variáveis de ambiente em produção
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-tk&-i3kn-^kzy0^ka)bvbq^m_bd^4922y+w+u0v8tqt#_0mr!2')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'pdsweb.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
    '*.app.github.dev',
    '*.github.dev'
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    "https://*.app.github.dev",
    "https://*.github.dev",
    "http://*.app.github.dev",
    "http://*.github.dev"
]

# Adicionar origens dinâmicas para Codespaces
if 'CODESPACE_NAME' in os.environ:
    codespace_name = os.getenv("CODESPACE_NAME")
    codespace_domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    codespace_url = f'https://{codespace_name}-8000.{codespace_domain}'
    if codespace_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(codespace_url)
    
    allowed_host = f'{codespace_name}-8000.{codespace_domain}'
    if allowed_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(allowed_host)

CSRF_FAILURE_VIEW = "usuarios.views.csrf_failure"

# ============================================================
# Messages
# ============================================================

MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}

# ============================================================
# Applications
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios.apps.UsuariosConfig',
    'comunidades',
    'conteudos',
    'principal',
]

# ============================================================
# Middleware
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Detectar IP dinâmico em Codespaces
if 'CODESPACE_NAME' in os.environ:
    import socket
    try:
        # Tenta obter o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        if ip_local not in INTERNAL_IPS:
            INTERNAL_IPS.append(ip_local)
    except:
        pass

ROOT_URLCONF = 'mysite.urls'

# ============================================================
# Templates
# ============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# ============================================================
# Database
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DJANGO_DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DJANGO_DB_USER', ''),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
        'HOST': os.getenv('DJANGO_DB_HOST', ''),
        'PORT': os.getenv('DJANGO_DB_PORT', ''),
    }
}

# ============================================================
# Password validation
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# Internationalization
# ============================================================

LANGUAGE_CODE = os.getenv('DJANGO_LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True



# ============================================================
# Default primary key
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# Custom user model
# ============================================================

AUTH_USER_MODEL = 'usuarios.Usuario'

# ============================================================
# Sessão e CSRF aprimorados para desenvolvimento
# ============================================================
'''
SESSION_COOKIE_AGE = 60 * 60 * 24
SESSION_SAVE_EVERY_REQUEST = False  # Evita conflitos de sessão com múltiplas requisições
CSRF_USE_SESSIONS = True
CSRF_COOKIE_AGE = 60 * 60 * 24

# Configuração segura para produção
SESSION_COOKIE_SECURE = os.getenv('DJANGO_SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.getenv('DJANGO_CSRF_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None
'''

# ============================================================
# Debug Toolbar Configuration
# ============================================================

# DEBUG_TOOLBAR não deve interferir no Django Admin
'''DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.logging.LoggingPanel',
    ],
    'EXCLUDE_URLS': [
        r'^/admin/',  # Desabilita debug_toolbar para /admin/
        r'^/admin/.*',
    ],
}'''

# ============================================================
# Static and Media
# ============================================================

# Media files (uploads de usuários)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# default static files settings for PythonAnywhere.
# see https://help.pythonanywhere.com/pages/DjangoStaticFiles for more info
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'principal:discussoes'