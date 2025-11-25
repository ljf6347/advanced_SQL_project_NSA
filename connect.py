import psycopg2

def add_database(username, password, database_name):
    return connect_to_database(username, password, database_name)

def connect_to_database(username, password, database_name):
    try:
        connection = psycopg2.connect(database = database_name, 
            user = username, 
            host= '127.0.0.1',
            password = password,
            port = 5432)
        print("DataBase connection Established")
        return connection
    except Exception:
        print("Connection failed")