from django.test import TestCase, override_settings
from django.test import Client

import mock

from .models import CountryWeather

# Create your tests here.


dummy_cache = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

class APIViewTestCase(TestCase):

    def setUp(self):
        self.weather_object = CountryWeather.objects.create(
            country_code='US',
            forecast_date='2021-11-01',
            weather='soso'
        )

        self.client = Client()

    @override_settings(CACHES=dummy_cache)
    @mock.patch('weather_app.main_api.views.ValidateData.connect_to_weather_api')
    @mock.patch('weather_app.main_api.views.ValidateData.validate_connection')
    def test_200_correct_data(self, mocked_function, mocked_connection):
        mocked_function.return_value = 18.0
        objects = len(CountryWeather.objects.all())
        self.assertEqual(objects, 1)

        response = self.client.get('/weather-forecast/?date=2021-11-01&country_code=US')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'forecast': 'soso'}, response.json())

        objects = len(CountryWeather.objects.all())
        self.assertEqual(objects, 1)

        self.assertTrue(mocked_function.was_called())


        response = self.client.get('/weather-forecast/?date=2021-11-01&country_code=US')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'forecast': 'soso'}, response.json())

        objects = len(CountryWeather.objects.all())
        self.assertEqual(objects, 1)


    @mock.patch('weather_app.main_api.views.ValidateData')
    def test_200_exists_in_cache(self, mocked_class):
        objects = len(CountryWeather.objects.all())
        self.assertEqual(objects, 1)


        with mock.patch('weather_app.main_api.views.cache') as mocked_cache:
            cache = {}

            def get(key, default=None):
                return cache.get(key, default)

            def _set(key, value, timeout=60):
                cache[key] = value

            mocked_cache.get = get
            mocked_cache.set = _set

            mocked_cache.set("US_2021-11-01", "soso")

            response = self.client.get('/weather-forecast/?date=2021-11-01&country_code=US')

            self.assertEqual(200, response.status_code)
            self.assertEqual({'forecast': 'soso'}, response.json())
            self.assertEqual(objects, len(CountryWeather.objects.all()))

            # validation class was called
            self.assertFalse(mocked_class.called)

    @mock.patch('weather_app.main_api.views.ValidateData')
    def test_200_set_to_cache(self, mocked_class):
        mocked_class().is_valid.return_value = True
        mocked_class().get_weather_mood.return_value = 'bad'

        with mock.patch('weather_app.main_api.views.cache') as mocked_cache:
            cache = {}

            def get(key, default=None):
                return cache.get(key, default)

            def _set(key, value, timeout=60):
                cache[key] = value

            mocked_cache.get = get
            mocked_cache.set = _set

            response = self.client.get('/weather-forecast/?date=2021-11-01&country_code=SK')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'forecast': 'bad'})

            self.assertEqual(mocked_cache.get('SK_2021-11-01'), 'bad')

            self.assertTrue(mocked_class.called)

    @override_settings(CACHES=dummy_cache)
    def test_400_old_date(self):
        preview_objects = CountryWeather.objects.all().count()
        self.assertEqual(preview_objects, 1)
        response = self.client.get('/weather-forecast/?date=2010-11-01&country_code=SK')

        self.assertEqual(response.status_code, 400)
        data_errors = response.json()['errors']
        self.assertEqual(data_errors['forecast_date'], 'Date must be greater than or equal to the current date.')

        self.assertEqual(preview_objects, CountryWeather.objects.all().count())

    @override_settings(CACHES=dummy_cache)
    def test_400_date_wrong_format(self):
        preview_objects = CountryWeather.objects.all().count()
        self.assertEqual(preview_objects, 1)
        response = self.client.get('/weather-forecast/?date=2021/01/01&country_code=SK')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(preview_objects, CountryWeather.objects.all().count())

    @override_settings(CACHES=dummy_cache)
    def test_400_country_code_not_provided(self):
        preview_objects = CountryWeather.objects.all().count()
        self.assertEqual(preview_objects, 1)
        response = self.client.get('/weather-forecast/?date=2021-11-01')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(preview_objects, CountryWeather.objects.all().count())

    @override_settings(CACHES=dummy_cache)
    def test_400_date_not_provided(self):
        preview_objects = CountryWeather.objects.all().count()
        self.assertEqual(preview_objects, 1)
        response = self.client.get('/weather-forecast/?country_code=US')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(preview_objects, CountryWeather.objects.all().count())

    @override_settings(CACHES=dummy_cache)
    def test_400_wrong_country_code(self):
        preview_objects = CountryWeather.objects.all().count()
        self.assertEqual(preview_objects, 1)
        response = self.client.get('/weather-forecast/?date=2021-12-01&country_code=JP')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(preview_objects, CountryWeather.objects.all().count())

    def test_post_request(self):
        response = self.client.post('/weather-forecast/?country_code=US')
        self.assertEqual(response.status_code, 405)
