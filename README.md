# Weather forecast API

It is a simple Django application that returns the forecast mood ('good', 'soso', 'bad') based on the provided country code (ISO_CODE_2) and date (YYYY-MM-DD).



## Requirements
- Python 3.6.9
- [Open weather API key](https://www.weatherapi.com/)
- [Redis server](https://redis.io/)

## Main commands

```python
# the key of third-part weather API
export WEATHER_API_KEY=<your-key>
```
```python
# add migrations to DB
python manage.py migrate
```
```python
# run tests
python manage.py test
```
```python
# request to server API
# request returns json format {'forecast': 'good'} like data
curl --request GET 'http://127.0.0.1:8000/weather-forecast/?date=<YYYY-MM-DD>&country_code=<AZ>'
```
```python
# run management command
# <AZ> - country code in ISO_CODE_2 format (US, SK, CZ)
python manage.py weather_forecast <YYYY-MM-DD> <AZ>
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.