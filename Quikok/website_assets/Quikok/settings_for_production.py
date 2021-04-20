from Quikok.settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': 'quikok_db_production',  
        'USER': 'root',
        'PASSWORD': '@Annie0800_GaryWx2003_tamiotsiu+#YT#',
        'HOST': '61.222.157.152',
        'PORT': '3306',
    }
}
DEBUG = False
ALLOWED_HOSTS = ['*']