from unittest.case import skip
from django.test import TestCase, Client


# Create your tests here.
# python manage.py test analytics/ --settings=Quikok.settings_for_test

class DASHBOARD_TESTS(TestCase):

    def setUp(self):
        self.client = Client()

    @skip
    def test_if_the_url_exists(self):
        response = \
            self.client.post(path='/analytics/quikok_dashboard/', data=dict())
        self.assertEqual(200, response.status_code)
        