
from Quikok.settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  
        'NAME': os.path.join(BASE_DIR, 'db_for_test.sqlite3'),
        'OPTIONS': {'charset':'utf8mb4'},
    }
}
