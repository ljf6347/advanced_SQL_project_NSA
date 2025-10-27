# types: missing records, value anomalies, outliers,
# date anomalies, categorical anomalies, schema changes, or a com-
# bination of these

def add_anomalies(connection, amount, type):
    match type:
        case "missing_records":
            remove_records(connection, amount)
        case "value_anomalies":
            add_value_anomalies(connection, amount)
        case "outliers":
            add_outliers(connection, amount)
        case "date_anomalies":
            add_date_anomalies(connection, amount)
        case "categorical_anomalies":
            add_categorical_anomalies(connection, amount)
        case "schema_anomalies":
            add_schema_anomalies(connection, amount)
        case _:
            print("Unknown anomaly type")

def remove_records(connection, amount):
    pass

def add_value_anomalies(connection, amount):
    pass

def add_outliers(connection, amount):
    pass

def add_date_anomalies(connection, amount):
    pass

def add_categorical_anomalies(connection, amount):
    pass

def add_schema_anomalies(connection, amount):
    pass

