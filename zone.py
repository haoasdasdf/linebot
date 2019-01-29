from timezonefinder import TimezoneFinder

from fire_db import DBAPI

tf = TimezoneFinder()

zone = tf.timezone_at(lng=100, lat=0)
print(zone)


if __name__ == "__main__":
    fire = DBAPI()
    