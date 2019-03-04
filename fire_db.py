import datetime
import logging
from timezonefinder import TimezoneFinder

import firebase_admin
from firebase_admin import credentials, firestore

from config import Config

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


# FIREBASE_KEY_URL = Config.FIREBASE_KEY_URL
class DBAPI():
	def __init__(self, app_name=None, *args, **kwargs):
		self.app_name = app_name if app_name is not None else 'default'
		self.cred = credentials.Certificate('firebasekey.json')
		self.FIREBASE_DATABASE_COLLECTION_NAME = Config.FIREBASE_CONFIG['COLLECTION_NAME']
		firebase_admin.initialize_app(self.cred)
		self.db = firestore.client()
		self.tf = TimezoneFinder()

	def add_user(self, data) :
		logger.info(data)
		if not self.check_is_exist(data['user_id']):
			logger.info('Register this user')
			try:
				data['active'] = True
				data['created_at'] = datetime.datetime.utcnow()
				data['updated_at'] = data['created_at']
				user = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user')
				user.document(data['user_id']).set(data)
			except Exception as e:
				logger.error('Add user failed')
				logger.error(e)
				return 'Some thing wrong, please try again'
			return 'Thank you for register your location'
		else:
			logger.info('Update user because already exist')
			try:
				data['active'] = True
				data['updated_at'] = datetime.datetime.utcnow()
				logger.info(data)
				self.update_user(data)
			except Exception as e:
				logger.error('Add user failed')
				logger.error(e)
				return 'Some thing wrong, please try again'
			return 'Thank you for updated your location'
		return

	def update_user(self, data):
		user = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user')
		try:
			user.document(data['user_id']).update(data)
			logger.info('updated data : {0}for {1}'.format(data, data['user_id']))
		except:
			logger.error('Failed to update {0}'.format(data['user_id']))

	def delete_user(self, user_id):
		if self.check_is_exist(user_id):
			logger.info('proccess to delete {0}'.format(user_id))
			try:
				user = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user')
				user.document(user_id).delete()
				return ('Your infomation was deleted')
			except Exception as e:
				logger.error('delete user failed')
				logger.error(e)
				return ('Some thing wrong, please try delete again')
		else:
			logger.info('You are not a register user')
			return ('You are not a register user')

	def get_location_info(self,user_id):
		if self.check_is_exist(user_id):
			logger.info('proccess to get location info for {0}'.format(user_id))
			try:
				users = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user').where('active', '==', True).where('user_id', '==', user_id).get()
				for user in users:
					print(user.to_dict().get('timezone'))
					data = {
					'latitude': user.to_dict()['latitude'],
					'longitude': user.to_dict()['longitude'],
					'timezone': 'Asia/Tokyo' if user.to_dict().get('timezone') is None else user.to_dict()['timezone'] 
					}
					logger.info('Got location info : {}'.format(data))
					return data

			except Exception as e:
				logger.info('Failed to get user location info {0}'.format(user_id))
				logger.error(e)
		else:
			logger.info('No data for user: {0}'.format(user_id))
		return None 

	def get_user_timezone(self, user_id):
		if self.check_is_exist(user_id):
			logger.info('proccess to get timezone info for {0}'.format(user_id))
			try:
				users = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user').where('user_id', '==', user_id).get()
				for user in users:
					timezone = user.to_dict().get('timezone')
					return timezone
			except:
				logger.error('Got error when get timezone info for {0}'.format(user_id))
				return None
		else:
			logger.info('No data for user: {0}'.format(user_id))
			return None 
		return None 

	def get_timezone_from_lat_long(self, latitude, longitude):
		try:
			timezone = self.tf.timezone_at(lat=latitude, lng=longitude)
			if timezone is None:
				raise ValueError('Timezone is None')
		except:
			logger.error('Get time zone from lat,long=({0}, {1}) failed, return default timezone Asia/Tokyo'.format(latitude, longitude))
			timezone = 'Asia/Tokyo'
		return timezone

	def activate_user(self, user_id):
		if self.check_is_exist(user_id):
			try:
				data = {}
				data['user_id'] = user_id
				data['active'] = True
				data['updated_at'] = datetime.datetime.utcnow()
				logger.info(data)
				self.update_user(data)
				logger.info('Active user: {0}'.format(user_id))
			except:
				logger.error('Failed to active user {0}'.format(user_id))
				return ('Failed to active user {0}'.format(user_id)) 
		else:
			logger.info('No data for user: {0}'.format(user_id))
			return ('No data for user: {0}'.format(user_id)) 
		return ('Active user: {0}'.format(user_id)) 

	def deactivate_user(self, user_id):
		if self.check_is_exist(user_id):
			try:
				data = {}
				data['user_id'] = user_id
				data['active'] = False
				data['updated_at'] = datetime.datetime.utcnow()
				logger.info(data)
				self.update_user(data)
				logger.info('Deactive user: {0}'.format(user_id))
			except:
				logger.error('Failed to deactive user {0}'.format(user_id))
				return ('Failed to deactive user {0}'.format(user_id))
		else:
			logger.info('No data for user: {0}'.format(user_id))
			return ('No data for user: {0}'.format(user_id))
		return ('Deactive user: {0}'.format(user_id))
	# users = db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user').get()
	# for user in users:
	#     print(user.to_dict())
	def get_active_users(self):
		active_user_id_list = []
		users = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user').where('active', '==', True).get()
		for user in users:
			logger.info(user.to_dict()['user_id'])
			active_user_id_list.append(user.to_dict()['user_id'])
		return (active_user_id_list)

	def check_is_exist(self, user_id):
		users = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user')
		check = users.where('user_id', '==', user_id).get()
		if len(list(check)) > 0:
			return True 
		return False

	def check_is_active(self, user_id):
		users = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user')
		check = users.where('user_id', '==', user_id).where('active', '==', True).get()
		if len(list(check)) > 0:
			return True 
		return False

	def check_this_user_count(self, user_id):
		users = self.db.collection(self.FIREBASE_DATABASE_COLLECTION_NAME).document(u'users').collection(u'user')
		check = users.where('user_id', '==', user_id).get()
		return len(list(check))

# For single test
if __name__ == "__main__":

	dummy_data = {
		'user_id': 'U816d9966f1e0af6c123cdb3a6522b7c4',
		'latitude': 35.691455,
		'longitude': 139.767683,
		'address': 'Japan, 〒101-0047 Tōkyō-to, Chiyoda-ku, Uchikanda, 2 Chome−12−５ 内山ビル'

	}
	do = DBAPI()

	# do.add_user(dummy_data)
	# logger.info(do.get_active_users())
	# logger.info(do.check_is_active('U816d9966f1e0af6c123cdb3a6522b7c4'))
	# logger.info(do.check_is_exist('U816d9966f1e0af6c123cdb3a6522b7c4'))
	# logger.info(do.get_location_info('U816d9966f1e0af6c123cdb3a6522b7c4'))
	# print(do.get_user_timezone('U816d9966f1e0af6c123cdb3a6522b7c4'))
	print(do.get_timezone_from_lat_long(33.807927, -117.922724))

