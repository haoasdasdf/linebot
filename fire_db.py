import logging
import os
import os.path
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
    
    def activate_user(self, user_id):
        pass

    def deactivate_user(self, user_id):
        pass
    # users = db.collection(u'linebot').document(u'users').collection(u'user').get()
    # for user in users:
    #     print(user.to_dict())
    def check_is_exist(self, user_id):
        users = self.db.collection(u'linebot').document(u'users').collection(u'user')
        check = users.where('user_id', '==', user_id).get()
        if len(list(check)) >0:
            return True
        return False