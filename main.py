import sys
import connect
import negative_selection

# MAIN PROGRAM
# Authors: 
#   Lucas Famous
#   Min Ko
#   Kavyaa Sheth

get_table_sql = """
    SELECT * FROM %s
"""

tables = ["customer", "lineitem", "orders"]
base_database_small = "csci_725_tpch_small"
base_database_medium = "csci_725_tpch_medium"
base_database_original = "csci_725_tpch_original"

detector_count = 1000

def execute_user_order(username, password, user_input):
    match user_input:
        case "detect_anomalies":
            method = input("Which statistical validation method would you like to use? (chi_square, Z_score, IQR, etc): " + "\n")
            # method = "IQR"
            # anomaly_type = "value"
            anomaly_type = input("What type of anomalies are you looking for? (value, outlier, date, or missing): " + "\n")
            if (anomaly_type == "missing"):
                percent = input("What percentage of missing values would you like to test for? (5, 10, 20, 50): " + "\n")
            data_size = input("What size of data would you like to test on? (small, medium, original): " + "\n")
            # data_size = "small"
            database_name = get_database_name(anomaly_type, data_size, percent if anomaly_type == "missing" else None)
            anomaly_connection = connect.add_database(username, password, database_name)
            precision = input("What size base table do you want? (small, medium, original): " + "\n")
            match precision:
                case "small":
                    base_database = base_database_small
                case "medium":
                    base_database = base_database_medium
                case _:
                    base_database = base_database_original
            main_connection = connect.add_database(username, password, base_database)

            for table in tables:
                print(f"Fetching data from table: {table}")
                main_cursor = main_connection.cursor()
                main_cursor.execute(get_table_sql % table)
                normal_records = list(main_cursor.fetchall())
                for r in range(len(normal_records)):
                    normal_records[r] = list(normal_records[r])
                anomaly_cursor = anomaly_connection.cursor()
                anomaly_cursor.execute(get_table_sql % table)
                anomaly_records = list(anomaly_cursor.fetchall())
                for r in range(len(anomaly_records)):
                    anomaly_records[r] = list(anomaly_records[r])

                features = [desc[0] for desc in main_cursor.description]

                negative_selection.detect_anomalies(normal_records, anomaly_records, features, detector_count, method=method)
        case "quit":
            if (anomaly_connection):
                anomaly_connection.close()
                print("Anomaly database connection closed")
            if (main_connection):
                main_connection.close()
                print("Main database connection closed")
            print("Connections closed")
            return
        
def get_database_name(anomaly_type, data_size, percent=None):
    database_name = f"csci_725_tpch_{anomaly_type}_"
    if (anomaly_type == "missing"):
        database_name += "record_"
    database_name += f"anomaly_{data_size}"
    if (anomaly_type == "missing"):
        database_name += f"_{percent}_percent"
    return database_name
    

if __name__ == "__main__":
    # args = sys.argv
    
    # # Requires username and password as arguments for Postgres
    # if len(args) < 3:
    #     print("Usage: pass the username and password for your postgres")
    # else:
    #     user_input = ""
    #     while user_input != "quit":
    #         user_input = input("What action do you want to take?" + "\n")
    #         execute_user_order(args[1], args[2], user_input)
    username = input("Enter your Postgres username: " + "\n")
    password = input("Enter your Postgres password: " + "\n")
    user_input = ""
    while user_input != "quit":
        # user_input = input("What action do you want to take?" + "\n")
        user_input = "detect_anomalies"
        execute_user_order(username, password, user_input)