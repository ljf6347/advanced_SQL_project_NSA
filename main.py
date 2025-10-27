import connect
import negative_selection
import anomalies
import load_data

# MAIN PROGRAM
# Authors: 
#   Lucas Famous
#   Min Ko
#   Kavyaa Sheth

def execute_user_order(connection, user_input):
    match user_input:
        case "add_anomalies":
            type = input("Enter the type of anomaly to add: ")
            amount = int(input("Enter the amount of anomalies to add: "))
            anomalies.add_anomalies(connection, amount, type)
        case "detect_anomalies":
            negative_selection.detect_anomalies(connection)
        case "load_initial_data":
            load_data.load_initial_data()
        case "load_data":
            load_data.load_data()
        case "save_data":
            load_data.save_initial_data()
        case "quit":
            connection.close()
            print("Connection closed")
            return

if __name__ == "__main__":
    main_connection = connect.add_connection()
    user_input = ""
    while user_input != "quit":
        user_input = input("What action do you want to take?" + "\n")
        execute_user_order(main_connection, user_input)
    main_connection.close()