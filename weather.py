import datetime
import json
import logging
import os

import dotenv
import requests
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

OPEN_WEATHER_MAP_API_KEY = os.environ.get('OPEN_WEATHER_MAP_API_KEY')
OPEN_WEATHER_MAP_BASE_URL = os.environ.get('OPEN_WEATHER_MAP_BASE_URL')
DARKSKY_API_SECRET_KEY = os.environ.get('DARKSKY_API_SECRET_KEY')
DARKSKY_API_BASE_URL = os.environ.get('DARKSKY_API_BASE_URL')

class Weather():
	def __init__(self, *args, **kwargs):
		self.OPEN_WEATHER_MAP_API_KEY = OPEN_WEATHER_MAP_API_KEY
		self.OPEN_WEATHER_MAP_BASE_URL = OPEN_WEATHER_MAP_BASE_URL
		self.DARKSKY_API_SECRET_KEY = DARKSKY_API_SECRET_KEY
		self.DARKSKY_API_BASE_URL = DARKSKY_API_BASE_URL
		self.geolocator = Nominatim(user_agent='LineBot')

	def get_city_name(self, latitude, longitude):
		'''
		Get city name and country code from geopy using Nominatim
		'''
		city_info = {}
		try:
			location = self.geolocator.reverse('{0}, {1}'.format(latitude, longitude))
			data = location.raw
			city_info = data['address']
			logger.info('Get location info')
			logger.info(city_info)
		except:
			logger.error('Failed to get city name')
			return None
		return city_info

	def get_weather_owm(self, city_name, country_code):
		'''
		Get weather info using  open weather map api
		'''
		url = self.OPEN_WEATHER_MAP_BASE_URL + 'q={0},{1}&appid={2}'.format(city_name, country_code, self.OPEN_WEATHER_MAP_API_KEY)
		try:
			response = requests.get(url)
			data = response.json()
			logger.info(json.dumps(data, indent=4))
			logger.info(data['cod'])
		except:
			logger.error('Failed to get weather from owm for {0}, {1}'.format(city_name, country_code))
		# for res in response.keys:
		# 	print(res)

	def get_weather_darksky(self, latitude, longitude, timestamp):
		url = self.DARKSKY_API_BASE_URL + '{0}/{1},{2},{3}?lang=ja&units=si'.format(self.DARKSKY_API_SECRET_KEY, latitude, longitude, timestamp)
		try:
			response = requests.get(url)
			data = response.json()

			logger.info('Got weather info from darksky')

		except:
			logger.error('Failed to get weather from darksky for {0}, {1}'.format(latitude, longitude))
			return None
		return data

	def temperature_f2c(self, fahrenheit):
		return (round((fahrenheit - 32) / 1.8))

	def get_weather(self, latitude, longitude, timestamp):
		'''
		return:
		{
			current_temp: {currently['temp']} @ {datetime}.format('HH:mm'),
			current_summary: {currently['summary']},
			daily_summary: {hourly['summary']},
			daily_humidity: {daily['data'][0]['humidity']} * 100
			max_temp: {daily['data'][0]['max_temp']} @ {datetime}.format('HH:mm'),
			min_temp: {daily['data'][0]['min_temp']} @ {datetime}.format('HH:mm'),
			max_apparent_temp: {daily['data'][0]['max_apparent_temp']} @ {datetime}.format('HH:mm'),
			min_apparent_temp: {daily['data']['min_apparent_temp']} @ {datetime}.format('HH:mm'),
			wind_speed: {daily['data'][0]['windSpeed']}
		
		}
		'''
		try:
			weather_data ={}
			darksky_data = self.get_weather_darksky(latitude, longitude, timestamp)
			if(darksky_data is not None):
				weather_data['current_temp'] = round(darksky_data['currently']['temperature'])
				weather_data['current_summary'] = darksky_data['currently']['summary']
				weather_data['daily_summary'] = darksky_data['hourly']['summary']
				weather_data['daily_humidity'] = round(darksky_data['daily']['data'][0]['humidity'] * 100)
				weather_data['max_temp'] = round(darksky_data['daily']['data'][0]['temperatureMax'])
				weather_data['min_temp'] = round(darksky_data['daily']['data'][0]['temperatureMin'])
				weather_data['max_apparent_temp'] = round(darksky_data['daily']['data'][0]['apparentTemperatureMax'])
				weather_data['min_apparent_temp'] = round(darksky_data['daily']['data'][0]['apparentTemperatureMin'])
				weather_data['wind_speed'] = darksky_data['daily']['data'][0]['windSpeed']
				return weather_data, self.get_city_name(latitude, longitude)
		except:
			logger.error('Failed to get weather data')
		return None, None
	def format_weather_data(self, weather_data, city_info):
		logger.info('Format weather data for send ')
		data = f'''
本日の天気予報です。
場所：{city_info['country']},{city_info['region']},{city_info['state']},{city_info['city']},〒{city_info['postcode']}
現在気温: {weather_data['current_temp']}°C, {weather_data['current_summary']}

今日は{weather_data['daily_summary']}
気温: {weather_data['min_temp']}°C ~ {weather_data['max_temp']}°C
体感気温: {weather_data['min_apparent_temp']}°C ~ {weather_data['max_apparent_temp']}°C
湿度: {weather_data['daily_humidity']}%
風速: {weather_data['wind_speed']} m/s
		     '''
		# sentence = [
		# 	'本日の天気予報です。',
		# 	f"場所：{city_info['country']},{city_info['region']},{city_info['state']},{city_info['city']},〒{city_info['postcode']}",
		# 	f"現在気温: {weather_data['current_temp']}°C, {weather_data['current_summary']}",
		# 	f"",
		# 	f"今日は{weather_data['daily_summary']}",
		# 	f"気温: {weather_data['min_temp']}°C ~ {weather_data['max_temp']}°C",
		# 	f"体感気温: {weather_data['min_apparent_temp']}°C ~ {weather_data['max_apparent_temp']}°C",
		# 	f"湿度: {weather_data['daily_humidity']}%",
		# 	f"風速: {weather_data['wind_speed']} m/s",
		# 	]
		# data = '\n'.join(sentence)
		return data


if __name__ == '__main__':

	dummy_location = {
		'latitude': 35.618364,
		'longitude': 139.68257
	}
	weather_dummy = {'current_temp': 9,
		'current_summary': '薄曇り',
			'daily_summary': '薄曇りが朝から始まり夕方まで続く。',
				'daily_humidity': 70,
					'max_temp': 10,
						'min_temp': 2,
					'max_apparent_temp': 10,
						'min_apparent_temp': 0,
							'wind_speed': 1.23
					}
	city_dummy = {
		'city': '目黒区', 'state': '東京都', 'region': '関東地方', 'postcode': '152-0003', 'country': '日本', 'country_code': 'jp'
	}
	timestamp = 1547153054
	# wea = Weather()
	# city = wea.get_city_name(dummy_location['latitude'], dummy_location['longitude'])
	# if(city is not None):
	# 	# wea.get_weather_owm(city['city'], city['country'])
	# print(wea.get_weather(dummy_location['latitude'], dummy_location['longitude'], int(datetime.datetime.now().timestamp())))
	# print(wea.format_weather_data(weather_dummy, city_dummy))
