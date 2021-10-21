from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .validator import ValidateData

# Create your views here.
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@require_http_methods(["GET"])
def get_weather(request):
    status = 200
    date = request.GET.get('date', '')
    country_code = request.GET.get('country_code', '').upper()
    cache_key = country_code + "_" + date
    forecast = cache.get(cache_key)
    if forecast:
        forecast = cache.get(cache_key)
        return JsonResponse({'forecast': forecast}, status=status)

    validator = ValidateData(country_code, date)
    if validator.is_valid():
        weather_mood = validator.get_weather_mood()
        json_data = {'forecast': weather_mood}
        cache.set(cache_key, weather_mood, timeout=CACHE_TTL)
    else:
        json_data = {'errors': validator.errors}
        status = 400

    return JsonResponse(json_data, status=status)
