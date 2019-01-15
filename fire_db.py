import logging
import os
import datetime
import dotenv
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

# FIREBASE_KEY_URL = os.environ.get('FIREBASE_KEY_URL')
class DBAPI(object):
	def __init__(self, *args, **kwargs):
		self.cred = credentials.Certificate('firebasekey.json')
		firebase_admin.initialize_app(self.cred)
		self.db = firestore.client()

	def add_user(self, data) :
		logger.info(data)
		if not self.check_is_exist(data['user_id']):
			logger.info('Register this user')
			try:
				data['active'] = True
				data['created_at'] = datetime.datetime.utcnow()
				data['updated_at'] = data['created_at']
				user = self.db.collection(u'linebot').document(u'users').collection(u'user')
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
		user = self.db.collection(u'linebot').document(u'users').collection(u'user')
		user.document(data['user_id']).update(data)

	def delete_user(self, user_id):
		if self.check_is_exist(user_id):
			logger.info('proccess to delete {0}'.format(user_id))
			try:
				user = self.db.collection(u'linebot').document(u'users').collection(u'user')
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
				users = self.db.collection(u'linebot').document(u'users').collection(u'user').where('active', '==', True).where('user_id', '==', user_id).get()
				for user in users:
					data = {
					'latitude': user.to_dict()['latitude'],
					'longitude': user.to_dict()['longitude']
					}
					logger.info('Got location info : {}'.format(data))
					return data

			except Exception as e:
				logger.info('Failed to get user location info {0}'.format(user_id))
				logger.error(e)
		else:
			logger.info('No data for user: {0}'.format(user_id))
		return None 

	def activate_user(self, user_id):
		pass

	def deactivate_user(self, user_id):
		pass
	# users = db.collection(u'linebot').document(u'users').collection(u'user').get()
	# for user in users:
	#     print(user.to_dict())
	def get_active_users(self):
		active_user_id_list = []
		users = self.db.collection(u'linebot').document(u'users').collection(u'user').where('active', '==', True).get()
		for user in users:
			logger.info(user.to_dict()['user_id'])
			active_user_id_list.append(user.to_dict()['user_id'])
		return (active_user_id_list)

	def check_is_exist(self, user_id):
		users = self.db.collection(u'linebot').document(u'users').collection(u'user')
		check = users.where('user_id', '==', user_id).get()
		if len(list(check)) > 0:
			return True 
		return False
	def check_this_user_count(self, user_id):
		users = self.db.collection(u'linebot').document(u'users').collection(u'user')
		check = users.where('user_id', '==', user_id).get()
		return len(list(check))

# For single test
if __name__ == "__main__":
	do = DBAPI()
	dummy_data = {
		'user_id': 'U816d9966f1e0af6c123cdb3a6522b7c4',
		'latitude': 35.691455,
		'longitude': 139.767683,
		'address': 'Japan, 〒101-0047 Tōkyō-to, Chiyoda-ku, Uchikanda, 2 Chome−12−５ 内山ビル'

	}

	# do.add_user(dummy_data)
	# logger.info(do.get_active_users())
	# logger.info(do.delete_user('U816d9966f1e0af6c123cdb3a6522b7c4'))
	# logger.info(do.check_is_exist('U816d9966f1e0af6c123cdb3a6522b7c4'))
	logger.info(do.get_location_info('U816d9966f1e0af6c123cdb3a6522b7c4'))
