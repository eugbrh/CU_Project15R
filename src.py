import requests
from api_keys import ACCUWEATHER_API_KEY

find_city = ''

class APIQuotaExceededError(Exception):
    pass

class Location:
    def __init__(self, accuweather_api_key, yandex_api_key):
        self.yandex_key = yandex_api_key
        self.accuweather_key = accuweather_api_key

    def request_to_yandex(self, city: str):
        params = {
            'apikey': self.yandex_key,
            'geocode': city,
            'lang': 'ru_RU',
            'format': 'json'
        }

        response = requests.get('https://geocode-maps.yandex.ru/1.x', params=params)

        if response.status_code != 200:
            print(f'Ошибка при получении данных. Код ошибки: {response.status_code}')
            return (f'Ошибка при получении данных. Код ошибки: {response.status_code}')
        return response.json()


    def get_coordinates(self, city: str):
        global find_city
        data = self.request_to_yandex(city)
        if data:
            try:
                coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                find_city = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
                lon, lat = coords.split(' ')
                lat = float(lat)
                # print(f"-------------lat------------")
                # print(f"------------{city}------------")
                # print(lat)
                lon = float(lon)
                # print(f"-------------lon------------")
                # print(f"------------{city}------------")
                # print(lon)
                return lat, lon
            except Exception as e:
                raise Exception(f"Ошибка получения координат: {e}")
        return None, None


    def get_location_key(self, lat, lon):
        params = {
            'apikey': self.accuweather_key,
            'q': f'{lat},{lon}'
        }
        response = requests.get('http://dataservice.accuweather.com/locations/v1/cities/geoposition/search', params=params)

        if response.status_code == 503 or 'ServiceUnavailable' in response.json().get('Code', ''):
            print("APIQuotaExceededError вызывается")
            raise APIQuotaExceededError("Запросы к API закончились")

        if response.status_code != 200 and response.status_code != 201:
            print('Ошибка при получении данных:', response.json())
            raise Exception(f'Ошибка при получении данных. Код ошибки: {response.status_code}')

        return response.json()['Key']

class Weather:
    def __init__(self, accuweather_api_key):
        self.accuweather_key = accuweather_api_key
        self.weather = {}

    def get_forecast_data(self, location_key, days=5):
        if days == 1:
            forecast_url = (
                f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
            )
        else:
            forecast_url = (
                f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
            )
        params = {
            "apikey": ACCUWEATHER_API_KEY,
            "language": "ru",
            "details": "true",
            "metric": "true",
        }
        response = requests.get(forecast_url, params=params)
        data = response.json()
        if data:
            return data
        else:
            return

    def check_bad_weather(self):
        weather = self.weather
        estimation = []

        if 'temperature' not in weather or 'wind_speed' not in weather or 'precipitation_prob' not in weather:
            raise KeyError("Недостаточно данных для оценки погодных условий.")

        if weather['temperature'] < 0 or weather['temperature'] > 35:
            estimation.append("Неприятная температура")
        if weather['wind_speed'] > 50:
            estimation.append("Очень сильный ветер")
        if weather['precipitation_prob'] > 70:
            estimation.append("Могут быть осадки")

        if estimation:
            answer = "Плохая погода: \n"
            for note in estimation:
                answer = answer + '   - ' + note + '\n'
            return answer
        else:
            return "Погода хорошая"