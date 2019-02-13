import datetime
import json
import logging
import os

import pytz
import requests
from geopy.geocoders import Nominatim

from config import Config

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)




OPEN_WEATHER_MAP_API_KEY = Config.OWM_API_CONFIG['KEY']
OPEN_WEATHER_MAP_BASE_URL = Config.OWM_API_CONFIG['BASE_URL']
DARKSKY_API_SECRET_KEY = Config.DARKSKYAPI_CONFIG['SECRET_KEY']
DARKSKY_API_BASE_URL = Config.DARKSKYAPI_CONFIG['BASE_URL']

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

	def get_weather_owm(self, latitude, longitude):
		'''
		Get weather info using  open weather map api
		'''
		url = self.OPEN_WEATHER_MAP_BASE_URL + 'weather?lat={0}&lon={1}&appid={2}'.format(latitude, longitude, self.OPEN_WEATHER_MAP_API_KEY)
		try:
			response = requests.get(url)
			data = response.json()
			# logger.info(json.dumps(data, indent=4))
			logger.info(data['cod'])
			return data
		except:
			logger.error('Failed to get weather from owm for {0}, {1}'.format(latitude, longitude))
		# for res in response.keys:
		# 	print(res)
			return None
		return None

	def get_weather_owm_5d(self, latitude, longitude):
		'''
		Get weather info using  open weather map api
		'''
		url = self.OPEN_WEATHER_MAP_BASE_URL + 'forecast?lat={0}&lon={1}&appid={2}'.format(latitude, longitude, self.OPEN_WEATHER_MAP_API_KEY)
		try:
			response = requests.get(url)
			data = response.json()
			# logger.info(json.dumps(data, indent=4))
			logger.info(data['cod'])
			return data
		except:
			logger.error('Failed to get weather from owm for {0}, {1}'.format(latitude, longitude))
		# for res in response.keys:
		# 	print(res)
			return None
		return None
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

	def get_direction(self, azimuth):
		direction = '未知'
		if azimuth < 23 or azimuth >= 338:
			direction = '北'
		elif azimuth < 68:
			direction = '東北'
		elif azimuth < 112:
			direction = '東'
		elif azimuth < 157:
			direction = '東南'
		elif azimuth < 202:
			direction = '南'
		elif azimuth < 247:
			direction = '西南'
		elif azimuth < 292:
			direction = '西'
		elif azimuth < 338:
			direction = '西北'
		return ('{0}方向'.format(direction))

	def change_to_local_time(self, timestamp, timezone):
		tz = pytz.timezone(timezone)
		local_time = datetime.datetime.fromtimestamp(timestamp, tz)
		return local_time


	def get_weather(self, latitude, longitude, timestamp):
		'''
		return:
		{
			current_temp: {currently['temp']} @ {datetime}.format('HH:mm'),
			current_summary: {currently['summary']},
			current_windBearing: {currently['windBearing']},
			daily_summary: {hourly['summary']},
			daily_humidity: {daily['data'][0]['humidity']} * 100
			max_temp: {daily['data'][0]['max_temp']} @ {datetime}.format('HH:mm'),
			min_temp: {daily['data'][0]['min_temp']} @ {datetime}.format('HH:mm'),
			max_apparent_temp: {daily['data'][0]['max_apparent_temp']} @ {datetime}.format('HH:mm'),
			min_apparent_temp: {daily['data']['min_apparent_temp']} @ {datetime}.format('HH:mm'),
			wind_speed: {daily['data'][0]['windSpeed']},
			daily_windBearing: {daily['windBearing']},
		
		}
		'''
		try:
			weather_data ={}
			darksky_data = self.get_weather_darksky(latitude, longitude, timestamp)
			if(darksky_data is not None):
				weather_data['current_temp'] = round(darksky_data['currently']['temperature'])
				weather_data['current_summary'] = darksky_data['currently']['summary']
				weather_data['current_windSpeed'] = darksky_data['currently']['windSpeed']
				weather_data['current_windBearing'] = darksky_data['currently']['windBearing'] if 'windBearing' in darksky_data['currently'] else None
				weather_data['daily_summary'] = darksky_data['hourly']['summary']
				weather_data['daily_humidity'] = round(darksky_data['daily']['data'][0]['humidity'] * 100)
				weather_data['max_temp'] = round(darksky_data['daily']['data'][0]['temperatureMax'])
				weather_data['min_temp'] = round(darksky_data['daily']['data'][0]['temperatureMin'])
				weather_data['max_apparent_temp'] = round(darksky_data['daily']['data'][0]['apparentTemperatureMax'])
				weather_data['min_apparent_temp'] = round(darksky_data['daily']['data'][0]['apparentTemperatureMin'])
				weather_data['wind_speed'] = darksky_data['daily']['data'][0]['windSpeed']
				weather_data['daily_windBearing'] = darksky_data['daily']['data'][0]['windBearing'] if 'windBearing' in darksky_data['daily']['data'][0] else None
				weather_data['sunriseTime'] = darksky_data['daily']['data'][0]['sunriseTime']
				weather_data['sunsetTime'] = darksky_data['daily']['data'][0]['sunsetTime']
				return weather_data, self.get_city_name(latitude, longitude)
		except:
			logger.error('Failed to get weather data')
		return None, None
	def format_weather_data(self, weather_data, city_info, timezone=None):

		logger.info('Format weather data for send ')
		if timezone is None:
			return

		city = city_info['city'] if city_info.get('city') is not None else (city_info['state_district'] if city_info.get('state_district') is not None else '')

		data = f'''
本日の天気予報です。
場所：{city_info['country']} {city_info['state'] if city_info.get('state') is not None else ''} {city} {city_info['town'] if city_info.get('town') is not None else ''}
現在気温: {weather_data['current_temp']}°C, {weather_data['current_summary']}
現在風速: {weather_data['current_windSpeed']} m/s, {self.get_direction(weather_data['current_windBearing'])}
		        
今日は{weather_data['daily_summary']}
気温: {weather_data['min_temp']}°C ~ {weather_data['max_temp']}°C
体感温度: {weather_data['min_apparent_temp']}°C ~ {weather_data['max_apparent_temp']}°C
湿度: {weather_data['daily_humidity']}%
風速: {weather_data['wind_speed']} m/s, {self.get_direction(weather_data['daily_windBearing'])}
日の出: {self.change_to_local_time(weather_data['sunriseTime'], timezone).strftime('%H:%M')}
日の入: {self.change_to_local_time(weather_data['sunsetTime'], timezone).strftime('%H:%M')}
		        '''
		return data


if __name__ == '__main__':
	# from worker import conn
	# from rq import Queue
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
	timestamp = datetime.datetime.now().timestamp()
	
	wea = Weather()
	# q = Queue(connection=conn)

	# result = q.enqueue('a','b')
	# city = wea.get_city_name(dummy_location['latitude'], dummy_location['longitude'])

	# j_data = open('./owm-result.json').read()
	# data = json.loads(j_data)
	# print(len(data['list']))
	# print(json.dumps(wea.get_weather_owm(dummy_location['latitude'], dummy_location['longitude']), indent=2))
	# test = datetime.timezone(datetime.timedelta(hours=9))
	# print(wea.change_to_local_time(int(datetime.datetime.now().timestamp()), 'Asia/Tokyo').strftime("%Y-%m-%d %H:%M"))
	# print(wea.get_weather(dummy_location['latitude'], dummy_location['longitude'], int(datetime.datetime.now().timestamp())))
	# weather_info, city_info = wea.get_weather(dummy_location['latitude'], dummy_location['longitude'], int(datetime.datetime.now().timestamp()))
	# print(wea.format_weather_data(weather_info, city_info))
