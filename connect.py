import pymongo
import logging
import auth

def add_database():
    return connect_to_database()

def connect_to_database():
    try:
        connection_string  = auth.getConnectionString()
        myclient = pymongo.MongoClient(connection_string, maxPoolSize=12, w='majority', connectTimeoutMS=2000)
        logging.getLogger("pymongo.command").setLevel(logging.ERROR)

        print("DataBase database Established")
        return myclient
    except Exception as e:
        raise Exception(f"database failed: {e}")