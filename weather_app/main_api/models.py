from django.db import models


# Create your models here.
class CountryWeather(models.Model):
    country_code = models.CharField(max_length=25)
    forecast_date = models.CharField(max_length=10)
    weather = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.country_code

    class Meta:
        verbose_name_plural = 'countries'
        unique_together = ('country_code', 'forecast_date')
