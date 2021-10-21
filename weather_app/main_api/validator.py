import re
from datetime import datetime
import requests

from django.conf import settings

from .models import CountryWeather

COUNTRIES = {
    'CZ': (49.817492, 15.472962),
    'US': (37.09024, -95.712891),
    'SK': (48.669026, 19.699024)
}

WEATHER_API_URL = 'http://api.weatherapi.com/v1/forecast.json'
KEY = settings.WEATHER_API_KEY

class ValidateData(object):

    errors = {}
    days = 10

    def __init__(self, country_code, date):
        self.country_code = country_code
        self.date = date
        self.is_provided = all([self.country_code, self.date])
        self.validate()

    def is_valid(self):
        return self.errors == {} and self.is_provided

    def validate(self):
        [getattr(self, method)() for method in dir(self) if method.startswith('validate_')]

    def validate_country_code(self):
        if not self.country_code:
            self.errors['country_code'] = 'Country code was not provided.'
            return
        if len(self.country_code) != 2:
            self.errors['country_code'] = "The length of the country code must be 2."
            return

        if self.country_code.upper() not in COUNTRIES:
            self.errors['country_code'] = 'Wrong country code.'
            return
        self.country_code = self.country_code.upper()

    def validate_date(self):
        result = re.findall(r'\d{4}-\d{2}-\d{2}', self.date)
        date = None
        if not result:
            self.errors['forecast_data'] = 'Date has invalid format. It should be YYYY-MM-DD format.'
            return
        try:
            date = datetime.strptime(self.date, '%Y-%m-%d')
        except ValueError as e:
            self.errors['forecast_date']: str(e)
            return

        if datetime.now().date() > date.date():
            self.errors['forecast_date'] = 'Date must be greater than or equal to the current date.'
            return
        # weather api allowes only 10 days feature weather
        self.days = min((date.date() - datetime.now().date()).days, self.days)
        return

    def validate_connection(self):
        test_query_params = "?key={KEY}&q=Lindon"
        r = requests.get(WEATHER_API_URL + test_query_params)
        if r.status_code != 200:
            self.errors['weather_api'] = r.json()
            return

    def get_weather_mood(self):
        weather_object, created = CountryWeather.objects.get_or_create(
            forecast_date=self.date,
            country_code=self.country_code
        )
        if created:

            latitude, langitude = COUNTRIES[self.country_code]

            query_params = f'?key={KEY}&day={self.day}&q={latitude},{langitude}'

            weather_api_url = WEATHER_API_URL + query_params
            avg_day_temperature = self.connect_to_weather_api(weather_api_url)

            if avg_day_temperature:
                weather_object.weather = self.get_mood(avg_day_temperature)
                weather_object.save()

        return weather_object.weather

    def get_mood(self, avg_day_temperature):
        weather = 'soso' if (
            avg_day_temperature > 10 and avg_day_temperature < 20
        ) else (
            'good' if avg_day_temperature > 20 else 'bad'
        )
        return weather

    def connect_to_weather_api(self, url):
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            self.errors['weather_api'] = data
            return
        else:
            data = response.json()
            if data['forecast'].get('forecastday'):
                avg_day_temperature = data['forecast']['forecastday'][0]['day']['avgtemp_c']
                return avg_day_temperature
        return
