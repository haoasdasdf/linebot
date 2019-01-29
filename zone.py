from timezonefinder import TimezoneFinder

from fire_db import DBAPI

tf = TimezoneFinder()

zone = tf.timezone_at(lng=100, lat=0)
print(zone)

# batch for add timezone for every user
if __name__ == "__main__":
    fire = DBAPI()
    users = fire.get_active_users()
    if len(users) > 0:
        result = []
        for user in users:
            result.append({'id':user, 'timezone': fire.get_user_timezone(user)})
            print(result)
            if fire.get_user_timezone(user) is None:
                info = fire.get_location_info(user)
                data ={
                    'user_id': user,
                    'timezone': fire.get_timezone_from_lat_long(info['latitude'], info['longitude'])
                }
                fire.update_user(data)
        

