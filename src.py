import requests

class Weather:
    def __init__(self, loc_key, accu_api_key):
        self.api_key = accu_api_key
        self.loc_key = loc_key
        self.weather = {}
        self.data = {}
    
    def get_current_weather_data(self):
        '''
        Получает погодные данные по location key
        '''
        params = {
        'apikey': self.api_key,
        'language': 'ru',
        'details': 'true'
        }
        response = requests.get(f"http://dataservice.accuweather.com/currentconditions/v1/{self.loc_key}", params=params)
        data = response.json()
        if data:
            self.weather['temperature'] = data[0]['Temperature']['Metric']['Value']
            self.weather['humidity'] = data[0]['RelativeHumidity']
            self.weather['wind_speed'] = data[0]['Wind']['Speed']['Metric']['Value']
            
            return data
        else:
            return None
        
    def get_forecast_data(self):
        params = {
        'apikey': self.api_key,
        'language': 'ru',
        'details': 'true',
        'metric': 'true'
        }
        response = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{self.loc_key}", params=params)
        data = response.json()
        if data:
            self.weather['precipitation_prob'] = data['DailyForecasts'][0]['Day']['PrecipitationProbability']
            return data
        else:
            return None
    
    def get_weather(self):
        self.get_current_weather_data()
        self.get_forecast_data()
        return self.weather
    
    def check_bad_weather(self):
        ''' 
        Функция для оценки неблагоприятных погодных условий 
        '''
        weather = self.weather
        warnings = []

        if weather['temperature'] < 0 or weather['temperature'] > 35:
            warnings.append("Неприятная температура.")
        if weather['wind_speed'] > 50:
            warnings.append("Сильный ветер.")
        if weather['precipitation_prob'] > 70:
            warnings.append("Высокая вероятность осадков.")

        if warnings:
            return "Неблагоприятные погодные условия: " + " ".join(warnings)
        else:
            return "Погодные условия благоприятные."

class Location:
    def __init__(self, accu_api_key, ya_api_key):
        self.accu = accu_api_key
        self.ya = ya_api_key
        self.lat = ''
        self.lon = ''
    
    def ya_request(self, city: str):
        params = {'apikey': self.ya,
                  'geocode': city,
                  'lang': 'ru_RU',
                  'kind': 'locality',
                  'format': 'json'}
        
        response = requests.get('https://geocode-maps.yandex.ru/1.x', params=params)

        if response.status_code != 200:
            print('Ошибка при получении данных:', response.json())
            return None

        return response.json()
    
    def get_coords(self, city: str):
        '''
        Возвращает координаты города
        '''
        data = self.ya_request(city)

        if data:
            try:
                coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                lon, lat = coords.split(' ')
                self.lat = lat
                self.lon = lon
                return str(lon), str(lat)
            except KeyError:
                print('Не удалось получить координаты')
                return None, None
        return None, None
    
    def get_key(self, city: str):
        '''
        Возвращает location key по координатам
        '''
        self.get_coords(city)
        params = {'apikey': self.accu,
                  'q': f'{self.lat},{self.lon}'}
        response = requests.get('http://dataservice.accuweather.com/locations/v1/cities/geoposition/search', params = params)

        if response.status_code != 200 and response.status_code != 201:
            print('Ошибка при получении данных:', response.json())
            return
        
        return response.json()['Key']
    
    def get_weather(self, city: str):
        '''
        Возвращает комментарий о погодных условиях и погодные условия в городе
        '''
        key = self.get_key(city)
        point = Weather(key, self.accu)
        data = point.get_weather()
        comment = point.check_bad_weather()
        return (comment, data)