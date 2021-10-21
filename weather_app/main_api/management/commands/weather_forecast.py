from django.core.management.base import BaseCommand, CommandError

from weather_app.main_api.validator import ValidateData


class Command(BaseCommand):
    help = 'Get forecast by provided country code and date.'

    def add_arguments(self, parser):
        parser.add_argument(
            'date', type=str)
        parser.add_argument(
            'country_code', type=str)

    def handle(self, *args, **options):
        date = options['date']
        country_code = options['country_code']

        try:
            validator = ValidateData(country_code=country_code, date=date)
            if validator.is_valid():
                self.stdout.write(
                    self.style.SUCCESS(
                        {'forecast': validator.get_weather_mood()}))
            else:
                self.stdout.write(
                    str({'errors': validator.errors})
                )

        except Exception as e:
            raise CommandError('Failed while retreiving data! {}'.format(e))
