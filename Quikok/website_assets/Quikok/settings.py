import os
import socket

DISABLED_EMAIL = os.environ.get('DISABLED_EMAIL', False) == 'true'
# 將 DISABLED_EMAIL 設做環境變數，假使這個值為真，則不與 gmail 連線進行 email 的「寄送」，
# 主要是為了解決開發/除錯時必定要有網路的問題。

DEV_MODE = os.environ.get('DEV_MODE', False) == 'true'
# 用它來取代 DEV_MODE 變數，當 DEV_MODE 為 True 時代表是開發環境，
# 除了會將異步改成同步執行以外，也會調整通知寄信的對象（不寄給老師、只寄給自己）。


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPEND_SLASH = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dhu80odw8@*7*o*oxznv+bkjsho1y@6#+6sodf*##d-cg9$o&r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatroom',
    'Quikok',
    'account',   # 用來處理註冊/個人訊息的呈現app
    'account_finance',  # 用來處理帳務(財務)資訊，如課程購買、退貨等等
    'lesson', # 課程商品頁
    'django_api', # 用來放api們
    'blog',  # quikok的文章專區
    'tinymce',
    'line_function',
    'analytics'
    # 'logentry_admin',  # This is to show all LogEntry objects in the Django admin site.
]
# 加入 logentry_admin 後，可能會遇到問題：
#   「Database returned an invalid datetime value. Are time zone definitions for your database installed?」
# 這時到 MySQL 部屬的主機，執行下列語句即可：
# mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql
# 即使出現 Warning: Unable to load '/usr/share/zoneinfo/iso3166.tab' as time zone. Skipping it. 之類的句子也無須擔心，
# 只是警告而已，應該還是有解決成功的。

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'Quikok.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['frontend/dist'],
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

WSGI_APPLICATION = 'Quikok.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': 'quikok_db',  # 資料庫/schema的名稱_development
        'USER': 'root',
        'PASSWORD': '@Annie0800_GaryWx2003_tamiotsiu+#YT#',
        'HOST': '61.222.157.152',
        'PORT': '3306',
    },
    # python manage.py migrate --database=production
    'production': {
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': 'quikok_db_production', 
        'USER': 'root',
        'PASSWORD': '@Annie0800_GaryWx2003_tamiotsiu+#YT#',
        'HOST': '61.222.157.152',
        'PORT': '3306',
    }
}
'''
將schema從A倒到B的方法:
    mysqldump  (--no-data) -u user -p database >database-schema.sql
    use schema2;
    source database-schema.sql;

    mysqldump -u root -p quikok_db_production > quikok_db_production_20201225.sql
'''


# channel settings
ASGI_APPLICATION = "Quikok.routing.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('localhost', 6379)],
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-Hant'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# 不加這一行會出現奇怪的錯誤，無法進行python manage.py collectstatic

# 在前端取用圖片的時候, /static/會取代在這邊註冊的路徑,所以要找以下路徑當中的檔案時,
# 路徑是 /static/開頭
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_files'),
    os.path.join(BASE_DIR, "frontend/dist"),
    os.path.join(BASE_DIR, "website_assets"),
    os.path.join(BASE_DIR, 'user_upload'),
    os.path.join(BASE_DIR, 'account/templates/account'),
    os.path.join(BASE_DIR, 'account_finance/templates/account_finance'),
    os.path.join(BASE_DIR, 'lesson/templates/lesson'),
    ]

# Add for vuejs
# STATICFILES_DIRS = [
 #     os.path.join(BASE_DIR, "frontend/dist"),  
 #     之後會在static/下建立對應的frontend/dist
# ]

# 存放使用者上傳的大頭照
MEDIA_URL = '/user_upload/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'user_upload')


#要寄信的相關設定

if DISABLED_EMAIL == False:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = socket.gethostbyname('smtp.gmail.com') # 改成這個會固定發IPv4,不用經IPv6,較快
    #EMAIL_HOST = 'smtp.gmail.com'  #SMTP伺服器
    EMAIL_PORT = 587  #TLS通訊埠號
    EMAIL_USE_TLS = True  #開啟TLS(傳輸層安全性)
    EMAIL_HOST_USER = 'quikok.taiwan@quikok.com'     # 'edony.ai.tech@gmail.com'  #寄件者電子郵件
    EMAIL_HOST_PASSWORD = 'jamthqadrfcxesdq'  #Gmail應用程式的密碼   

