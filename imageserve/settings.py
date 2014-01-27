# Django settings for imageserve project.
import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

JSON_INTERFACE = "http://openmind-ismi-dev.mpiwg-berlin.mpg.de/om4-ismi/jsonInterface?"
OBJECT_DATA = "/data-proxy"
IIPSERVER_URL = "https://images.rasi.mcgill.ca/fcgi-bin/iipsrv.fcgi"
IMG_DIR = "/data7/srv/images"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

REST_FRAMEWORK = {
    'PAGINATE_BY': 50,                 # Default to 10
    'PAGINATE_BY_PARAM': 'page_size',  # Allow client to override, using `?page_size=xxx`.
    'MAX_PAGINATE_BY': 100,             # Maximum limit allowed when using `?page_size=xxx`.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

NO_DATA_MSG = "Data not entered"

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'imageserve_app',
        'USER': 'ahankins',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Montreal'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_PATH + '/static',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't9vz!s()ix87g4+g%ji!c%w8997os$gz3yib%kwiwv+_-p&amp;f@('

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.static',
    "django.core.context_processors.request",
    "imageserve.context_processors.diva.diva_settings"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware'
)


ROOT_URLCONF = 'imageserve.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'imageserve.wsgi.application'

TEMPLATE_DIRS = (
    PROJECT_PATH,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django_extensions',
    'bootstrap-pagination',
    'south',
    'guardian',
    'imageserve',
    'rest_framework'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default
    'guardian.backends.ObjectPermissionBackend',
)

ANONYMOUS_USER_ID = -1

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

STABI_CODICES = [
    "Diez_A_quart_49",
    "Glaser_6",
    "Glaser_21",
    "Glaser_40",
    "Glaser_83",
    "Glaser_103",
    "Glaser_163",
    "Glaser_227",
    "Glaser_239",
    "Landberg_33",
    "Landberg_56",
    "Landberg_58",
    "Landberg_63",
    "Landberg_68",
    "Landberg_71",
    "Landberg_108",
    "Landberg_110",
    "Landberg_131",
    "Landberg_132",
    "Landberg_144",
    "Landberg_199",
    "Landberg_221",
    "Landberg_390",
    "Landberg_493",
    "Landberg_517",
    "Landberg_526a",
    "Landberg_526b",
    "Landberg_526c",
    "Landberg_528",
    "Landberg_548",
    "Landberg_558",
    "Landberg_563",
    "Landberg_574",
    "Landberg_597",
    "Landberg_599",
    "Landberg_608",
    "Landberg_656",
    "Landberg_669",
    "Landberg_700",
    "Landberg_720",
    "Landberg_721",
    "Landberg_724",
    "Landberg_725",
    "Landberg_734",
    "Landberg_789",
    "Landberg_801",
    "Landberg_808",
    "Landberg_880",
    "Landberg_901",
    "Landberg_953",
    "Landberg_1038",
    "Landberg_1045",
    "Landberg_1047",
    "Minutoli_190",
    "Ms_or_fol_34",
    "Ms_or_fol_256",
    "Ms_or_oct_109",
    "Ms_or_oct_200",
    "Ms_or_oct_252",
    "Ms_or_oct_273",
    "Ms_or_oct_274",
    "Ms_or_oct_275",
    "Ms_or_quart_98",
    "Ms_or_quart_99",
    "Ms_or_quart_100",
    "Ms_or_quart_101",
    "Ms_or_quart_103",
    "Ms_or_quart_119",
    "Ms_or_quart_180b",
    "Ms_or_quart_559",
    "Ms_or_quart_690",
    "Ms_or_quart_704",
    "Ms_or_quart_728",
    "Ms_or_quart_733",
    "Petermann_II_79",
    "Petermann_II_124",
    "Petermann_II_228",
    "Petermann_II_369",
    "Petermann_II_396",
    "Petermann_II_402",
    "Petermann_II_466",
    "Petermann_II_681",
    "Petermann_I_62",
    "Petermann_I_67",
    "Petermann_I_315",
    "Petermann_I_542",
    "Petermann_I_669",
    "Petermann_I_670",
    "Petermann_I_671",
    "Petermann_I_672",
    "Petermann_I_673",
    "Petermann_I_674",
    "Sprenger_1824a",
    "Sprenger_1824b",
    "Sprenger_1825",
    "Sprenger_1832-1833",
    "Sprenger_1835",
    "Sprenger_1837",
    "Sprenger_1838",
    "Sprenger_1841",
    "Sprenger_1844",
    "Sprenger_1847a",
    "Sprenger_1847b",
    "Sprenger_1848",
    "Sprenger_1849",
    "Sprenger_1855",
    "Sprenger_1857",
    "Sprenger_1858",
    "Sprenger_1863",
    "Sprenger_1866",
    "Sprenger_1869",
    "Sprenger_1872",
    "Sprenger_1876",
    "Sprenger_1877",
    "Sprenger_1979",
    "Wetzstein_II_131",
    "Wetzstein_II_1127",
    "Wetzstein_II_1128",
    "Wetzstein_II_1129",
    "Wetzstein_II_1130",
    "Wetzstein_II_1131",
    "Wetzstein_II_1132",
    "Wetzstein_II_1133",
    "Wetzstein_II_1134",
    "Wetzstein_II_1135",
    "Wetzstein_II_1136",
    "Wetzstein_II_1138",
    "Wetzstein_II_1138a",
    "Wetzstein_II_1139",
    "Wetzstein_II_1142",
    "Wetzstein_II_1143",
    "Wetzstein_II_1146",
    "Wetzstein_II_1148",
    "Wetzstein_II_1149",
    "Wetzstein_II_1150",
    "Wetzstein_II_1152",
    "Wetzstein_II_1713",
    "Wetzstein_II_1717",
    "Wetzstein_II_1725",
    "Wetzstein_II_1734",
    "Wetzstein_II_1736a",
    "Wetzstein_II_1746",
    "Wetzstein_II_1763",
    "Wetzstein_II_1766",
    "Wetzstein_II_1772",
    "Wetzstein_II_1782",
    "Wetzstein_II_1791",
    "Wetzstein_II_1809",
    "Wetzstein_II_1810",
    "Wetzstein_II_1811",
    "Wetzstein_II_1813",
    "Wetzstein_II_1817",
    "Wetzstein_II_1825",
    "Wetzstein_II_1834",
    "Wetzstein_II_1869",
    "Wetzstein_I_90",
    "Wetzstein_I_175",
    "Wetzstein_I_179",
    "Wetzstein_I_191",
    "Wetzstein_I_193"
]




