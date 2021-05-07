
from Quikok.settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': 'quikok_db_test',  
        'USER': 'root',
        'PASSWORD': '0800',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'TEST_CHARSET': 'utf8',        
        'TEST_COLLATION': 'utf8_general_ci',
        'OPTIONS': {'charset':'utf8mb4'},
    }
}
