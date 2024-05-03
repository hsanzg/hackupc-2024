from pymongo import MongoClient
import os
import datetime
import fileinput

def connect():
  conn_string = os.environ['MONGO_CONN']
  db_name = os.environ['MONGO_DB']
  coll_name = os.environ['MONGO_COLL']
  print(f'connecting to {conn_string}, db={db_name}, collection={coll_name}')
  client = MongoClient(conn_string)
  print('success!')

  # Our database and collection are both called "workplace"
  db = client[db_name]
  if coll_name not in db.list_collection_names():
    collection = db.create_collection(coll_name, timeseries={
      'timeField': 'timestamp',
      'metaField': 'metadata',
      'granularity': 'seconds'
    })
    print(f'created {coll_name}')
  else:
    collection = db[coll_name]
  return collection

# warning: this method modifies the passed `metrics` object
def upload(collection, metrics):
  time = datetime.now() # todo: utcnow?
  count = len(metrics.keys())
  print(f'[{time}] uploading {count} metrics')
  metrics['metadata'] = {}
  metrics['timestamp'] = time
  collection.insert_one(metrics)

if __name__ == '__main__':
  print('starting up')
  collection = connect()
  # Read numbers output through serial from ESP32 board.
  for line in fileinput.input(encoding='utf-8'):
    raw_temp, raw_hum = line.split(',')
    upload(collection, {
      'temp': float(raw_temp),
      'hum': float(raw_hum)
    })
