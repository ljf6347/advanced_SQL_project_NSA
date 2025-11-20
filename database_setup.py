"""
This file can be used to Setup the TPC-H database
we need for this project. This script will do the following:
1. Setup 3 Databases with different TPC-H sizes: Original (with all the data), Medium (10% of Original data) and Small (1% of Original Data)
2. For Each Anomaly, we need a separate database and need to introduce anomaly in that data. So this script setups databases for anomaly and creates the anomaly
3. Creates .tbl files for all the databses we created and also created a pg_dump file.

Note: Before running this script it is expected that:
1. You have postgres install and have setup your username and password with appropriate permissions.
2. You will need psycopg2 package to connect to postgres.

Author: Kavyaa Sheth
"""
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def create_database(dbname, username, password):
    """
    Creates a new database in postgres and gives appropriate permissions to it to your user.
    :param dbname: String value for the name you want to give to your database
    :param username: String value of your username
    :param password: String value of you password
    :returns bool: status of whether db is created
    """
    conn = psycopg2.connect(dbname="postgres", user=username, password=password, host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur=conn.cursor()
    
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;",(dbname,))
    exists=cur.fetchone()
    
    if not exists:
        cur.execute(f"CREATE DATABASE {dbname};")
        cur.execute(f"GRANT ALL PRIVILEGES ON database {dbname} TO {username};")
        print(f"Database '{dbname}' CREATED Successfully!!")
        cur.close()
        conn.close()
        return True
    else:
        print(f"Ooooopsss Database '{dbname}' already EXISTS!!")
        cur.close()
        conn.close()
        return False
    
def setup_database_with_original_data(dbname, filepath_dir, username, password):
    """
    Creates a new database in postgres and gives appropriate permissions to it to your user.
    :param name: String value for the name you want to give to your database
    :param username: String value of your username
    :param password: String value of you password 
    """
    # Create db with name dbname
    create_database(dbname, username, password)
    
    # Load Data
    customer_file_path = os.path.join(filepath_dir,"customer.tbl")
    order_file_path = os.path.join(filepath_dir,"orders.tbl")
    lineitem_file_path = os.path.join(filepath_dir,"lineitem.tbl")
    
    print(customer_file_path)
    print(order_file_path)
    print(lineitem_file_path)
    
    conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
    cur=conn.cursor()

    # create tables
    cur.execute("CREATE TABLE CUSTOMER ( C_CUSTKEY INTEGER NOT NULL, C_NAME VARCHAR(25) NOT NULL,C_ADDRESS VARCHAR(40) NOT NULL,C_NATIONKEY INTEGER NOT NULL,C_PHONE CHAR(15) NOT NULL,C_ACCTBAL DECIMAL(15,2) NOT NULL, C_MKTSEGMENT CHAR(10) NOT NULL,C_COMMENT VARCHAR(117) NOT NULL);")
    cur.execute("CREATE TABLE ORDERS  ( O_ORDERKEY INTEGER NOT NULL, O_CUSTKEY INTEGER NOT NULL, O_ORDERSTATUS CHAR(1) NOT NULL, O_TOTALPRICE DECIMAL(15,2) NOT NULL, O_ORDERDATE DATE NOT NULL, O_ORDERPRIORITY CHAR(15) NOT NULL, O_CLERK CHAR(15) NOT NULL, O_SHIPPRIORITY INTEGER NOT NULL, O_COMMENT VARCHAR(79) NOT NULL);")
    cur.execute("CREATE TABLE LINEITEM ( L_ORDERKEY    INTEGER NOT NULL, L_PARTKEY INTEGER NOT NULL, L_SUPPKEY INTEGER NOT NULL, L_LINENUMBER INTEGER NOT NULL, L_QUANTITY DECIMAL(15,2) NOT NULL, L_EXTENDEDPRICE DECIMAL(15,2) NOT NULL, L_DISCOUNT DECIMAL(15,2) NOT NULL, L_TAX DECIMAL(15,2) NOT NULL, L_RETURNFLAG CHAR(1) NOT NULL, L_LINESTATUS CHAR(1) NOT NULL, L_SHIPDATE DATE NOT NULL, L_COMMITDATE DATE NOT NULL, L_RECEIPTDATE DATE NOT NULL, L_SHIPINSTRUCT CHAR(25) NOT NULL, L_SHIPMODE CHAR(10) NOT NULL, L_COMMENT VARCHAR(44) NOT NULL);")

    # Load Data
    with open(customer_file_path, "r") as f:
        cur.copy_expert(
            "COPY customer FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )
    with open(order_file_path, "r") as f:
        cur.copy_expert(
            "COPY orders FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )
    with open(lineitem_file_path, "r") as f:
        cur.copy_expert(
            "COPY lineitem FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )
    # cur.execute(f"\copy customer FROM '{customer_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    # cur.execute(f"\copy customer FROM '{order_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    # cur.execute(f"\copy customer FROM '{lineitem_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    conn.commit()
    cur.close()
    conn.close()
    
def setup_database_with_medium_data(dbname, filepath_dir, username, password):
    """
    Creates a new database in postgres and gives appropriate permissions to it to your user.
    :param name: String value for the name you want to give to your database
    :param username: String value of your username
    :param password: String value of you password 
    """
    # Create db with name dbname
    create_database(dbname, username, password)
    
    # Load Data
    customer_file_path = os.path.join(filepath_dir,"customer_medium.tbl")
    order_file_path = os.path.join(filepath_dir,"orders_medium.tbl")
    lineitem_file_path = os.path.join(filepath_dir,"lineitem_medium.tbl")
    
    print(customer_file_path)
    print(order_file_path)
    print(lineitem_file_path)
    
    
    conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
    cur=conn.cursor()

    # create tables
    cur.execute("CREATE TABLE CUSTOMER ( C_CUSTKEY INTEGER NOT NULL, C_NAME VARCHAR(25) NOT NULL,C_ADDRESS VARCHAR(40) NOT NULL,C_NATIONKEY INTEGER NOT NULL,C_PHONE CHAR(15) NOT NULL,C_ACCTBAL DECIMAL(15,2) NOT NULL, C_MKTSEGMENT CHAR(10) NOT NULL,C_COMMENT VARCHAR(117) NOT NULL);")
    cur.execute("CREATE TABLE ORDERS  ( O_ORDERKEY INTEGER NOT NULL, O_CUSTKEY INTEGER NOT NULL, O_ORDERSTATUS CHAR(1) NOT NULL, O_TOTALPRICE DECIMAL(15,2) NOT NULL, O_ORDERDATE DATE NOT NULL, O_ORDERPRIORITY CHAR(15) NOT NULL, O_CLERK CHAR(15) NOT NULL, O_SHIPPRIORITY INTEGER NOT NULL, O_COMMENT VARCHAR(79) NOT NULL);")
    cur.execute("CREATE TABLE LINEITEM ( L_ORDERKEY    INTEGER NOT NULL, L_PARTKEY INTEGER NOT NULL, L_SUPPKEY INTEGER NOT NULL, L_LINENUMBER INTEGER NOT NULL, L_QUANTITY DECIMAL(15,2) NOT NULL, L_EXTENDEDPRICE DECIMAL(15,2) NOT NULL, L_DISCOUNT DECIMAL(15,2) NOT NULL, L_TAX DECIMAL(15,2) NOT NULL, L_RETURNFLAG CHAR(1) NOT NULL, L_LINESTATUS CHAR(1) NOT NULL, L_SHIPDATE DATE NOT NULL, L_COMMITDATE DATE NOT NULL, L_RECEIPTDATE DATE NOT NULL, L_SHIPINSTRUCT CHAR(25) NOT NULL, L_SHIPMODE CHAR(10) NOT NULL, L_COMMENT VARCHAR(44) NOT NULL);")

    # Load Data
    with open(customer_file_path, "r") as f:
        cur.copy_expert(
            "COPY customer FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )
    with open(order_file_path, "r") as f:
        cur.copy_expert(
            "COPY orders FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )
    with open(lineitem_file_path, "r") as f:
        cur.copy_expert(
            "COPY lineitem FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )

    # cur.execute(f"\copy customer FROM '{customer_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    # cur.execute(f"\copy customer FROM '{order_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    # cur.execute(f"\copy customer FROM '{lineitem_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    
    conn.commit()
    cur.close()
    conn.close() 
    
def setup_database_with_small_data(dbname, filepath_dir, username, password):
    """
    Creates a new database in postgres and gives appropriate permissions to it to your user.
    :param name: String value for the name you want to give to your database
    :param username: String value of your username
    :param password: String value of you password 
    """
    # Create db with name dbname
    create_database(dbname, username, password)
    
    # Load Data
    customer_file_path = os.path.join(filepath_dir,"customer_small.tbl")
    order_file_path = os.path.join(filepath_dir,"orders_small.tbl")
    lineitem_file_path = os.path.join(filepath_dir,"lineitem_small.tbl")
    
    print(customer_file_path)
    print(order_file_path)
    print(lineitem_file_path)
    
    conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
    cur=conn.cursor()

    # create tables
    cur.execute("CREATE TABLE CUSTOMER ( C_CUSTKEY INTEGER NOT NULL, C_NAME VARCHAR(25) NOT NULL,C_ADDRESS VARCHAR(40) NOT NULL,C_NATIONKEY INTEGER NOT NULL,C_PHONE CHAR(15) NOT NULL,C_ACCTBAL DECIMAL(15,2) NOT NULL, C_MKTSEGMENT CHAR(10) NOT NULL,C_COMMENT VARCHAR(117) NOT NULL);")
    cur.execute("CREATE TABLE ORDERS  ( O_ORDERKEY INTEGER NOT NULL, O_CUSTKEY INTEGER NOT NULL, O_ORDERSTATUS CHAR(1) NOT NULL, O_TOTALPRICE DECIMAL(15,2) NOT NULL, O_ORDERDATE DATE NOT NULL, O_ORDERPRIORITY CHAR(15) NOT NULL, O_CLERK CHAR(15) NOT NULL, O_SHIPPRIORITY INTEGER NOT NULL, O_COMMENT VARCHAR(79) NOT NULL);")
    cur.execute("CREATE TABLE LINEITEM ( L_ORDERKEY    INTEGER NOT NULL, L_PARTKEY INTEGER NOT NULL, L_SUPPKEY INTEGER NOT NULL, L_LINENUMBER INTEGER NOT NULL, L_QUANTITY DECIMAL(15,2) NOT NULL, L_EXTENDEDPRICE DECIMAL(15,2) NOT NULL, L_DISCOUNT DECIMAL(15,2) NOT NULL, L_TAX DECIMAL(15,2) NOT NULL, L_RETURNFLAG CHAR(1) NOT NULL, L_LINESTATUS CHAR(1) NOT NULL, L_SHIPDATE DATE NOT NULL, L_COMMITDATE DATE NOT NULL, L_RECEIPTDATE DATE NOT NULL, L_SHIPINSTRUCT CHAR(25) NOT NULL, L_SHIPMODE CHAR(10) NOT NULL, L_COMMENT VARCHAR(44) NOT NULL);")

    # Load Data
    with open(customer_file_path, "r") as f:
        cur.copy_expert(
            "COPY customer FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )
    with open(order_file_path, "r") as f:
        cur.copy_expert(
            "COPY orders FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )
    with open(lineitem_file_path, "r") as f:
        cur.copy_expert(
            "COPY lineitem FROM STDIN WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false)", f
        )

    # cur.execute(f"\copy customer FROM '{customer_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    # cur.execute(f"\copy customer FROM '{order_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")
    # cur.execute(f"\copy customer FROM '{lineitem_file_path}' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);")

    conn.commit()
    cur.close()
    conn.close()

def missing_record_anomaly(anomaly_percent, dbname, username, password):
    conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
    cur=conn.cursor()
    cur.execute(f"delete from customer where random() <= {anomaly_percent};")
    cur.execute(f"delete from orders where random() <= {anomaly_percent};")
    cur.execute(f"delete from lineitem where random() <= {anomaly_percent};")
    conn.commit()
    cur.close()
    conn.close()

def value_anomaly(dbname, username, password):
    conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
    cur=conn.cursor()
    cur.execute("UPDATE customer SET c_nationkey = CEIL(c_nationkey * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    cur.execute("UPDATE customer SET c_acctbal = (c_acctbal * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    
    cur.execute("UPDATE orders SET o_totalprice = (o_totalprice * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    cur.execute("UPDATE orders SET o_shippriority = CEIL(o_shippriority * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    
    cur.execute("UPDATE lineitem SET l_linenumber = CEIL(l_linenumber * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    cur.execute("UPDATE lineitem SET l_quantity = (l_quantity * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    cur.execute("UPDATE lineitem SET l_extendedprice = (l_extendedprice * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    cur.execute("UPDATE lineitem SET l_discount = (l_discount * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    cur.execute("UPDATE lineitem SET l_tax = (l_tax * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;")
    conn.commit()
    cur.close()
    conn.close()
    
def outlier_anomaly(dbname, username, password):
    conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
    cur=conn.cursor()
    cur.execute("UPDATE orders SET o_totalprice = 100*o_totalprice WHERE random() < 0.2;")
    cur.execute("UPDATE lineitem SET l_tax = 100*l_tax WHERE random() < 0.2;")
    cur.execute("UPDATE lineitem SET l_extendedprice = 100*l_extendedprice WHERE random() < 0.2;")
    conn.commit()
    cur.close()
    conn.close()
    
def date_anomaly(dbname, username, password):
    conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
    cur=conn.cursor()
    cur.execute(f"UPDATE lineitem SET l_shipdate = '1998-01-01', l_receiptdate = '1996-01-05' WHERE random() < 0.20;")
    conn.commit()
    cur.close()
    conn.close()

def anomaly_database_setup(filepath_dir, username, password):
    # Missing Record Anomaly Database
    anomaly_percents = [0.05, 0.10, 0.2, 0.5]
    labels = ["5_percent", "10_percent", "20_percent", "50_percent"]
    for i, anomaly_percent in enumerate(anomaly_percents):
        missing_dbname = "csci_725_tpch_missing_record_anomaly_original_"+labels[i]
        setup_database_with_original_data(missing_dbname, filepath_dir, username, password)
        missing_record_anomaly(anomaly_percent, missing_dbname, username, password)

        missing_dbname = "csci_725_tpch_missing_record_anomaly_medium_"+labels[i]
        setup_database_with_medium_data(missing_dbname, filepath_dir, username, password)
        missing_record_anomaly(anomaly_percent, missing_dbname, username, password)

        missing_dbname = "csci_725_tpch_missing_record_anomaly_small_"+labels[i]
        setup_database_with_small_data(missing_dbname, filepath_dir, username, password)
        missing_record_anomaly(anomaly_percent, missing_dbname, username, password)
    
    print("Missing Record Anomaly Databases Created Successfully!")
    
    # Value Anomaly Database
    value_dbname = "csci_725_tpch_value_anomaly_original"
    setup_database_with_original_data(value_dbname, filepath_dir, username, password)
    value_anomaly(value_dbname, username, password)

    value_dbname = "csci_725_tpch_value_anomaly_medium"
    setup_database_with_medium_data(value_dbname, filepath_dir, username, password)
    value_anomaly(value_dbname, username, password)

    value_dbname = "csci_725_tpch_value_anomaly_small"
    setup_database_with_small_data(value_dbname, filepath_dir, username, password)
    value_anomaly(value_dbname, username, password)
    
    print("Value Anomaly Databases Created Successfully!")

    # Outlier Anomaly Database
    outlier_dbname = "csci_725_tpch_outlier_anomaly_original"
    setup_database_with_original_data(outlier_dbname, filepath_dir, username, password)
    outlier_anomaly(outlier_dbname, username, password)

    outlier_dbname = "csci_725_tpch_outlier_anomaly_medium"
    setup_database_with_medium_data(outlier_dbname, filepath_dir, username, password)
    outlier_anomaly(outlier_dbname, username, password)

    outlier_dbname = "csci_725_tpch_outlier_anomaly_small"
    setup_database_with_small_data(outlier_dbname, filepath_dir, username, password)
    outlier_anomaly(outlier_dbname, username, password)
    
    print("Outlier Anomaly Databases Created Successfully!")

    # Date Anomaly Database
    date_dbname = "csci_725_tpch_date_anomaly_original"
    setup_database_with_original_data(date_dbname, filepath_dir, username, password)
    date_anomaly(date_dbname, username, password)

    date_dbname = "csci_725_tpch_date_anomaly_medium"
    setup_database_with_medium_data(date_dbname, filepath_dir, username, password)
    date_anomaly(date_dbname, username, password)

    date_dbname = "csci_725_tpch_date_anomaly_small"
    setup_database_with_small_data(date_dbname, filepath_dir, username, password)
    date_anomaly(date_dbname, username, password)
    print("Date Anomaly Databases Created Successfully!")

def test_connection(dbname, username, password):
    try:
        conn = psycopg2.connect(dbname=dbname, user=username, password=password, host="localhost", port="5432")
        print("Connection to database ", dbname, " successful")
        conn.close()
    except Exception as e:
        print("Error connecting to database ", dbname)
        print(e)

def main(args):
    datafile_location = args[1]
    username = args[2]
    password = args[3]
    storefile_location = None
    
    if len(args) > 4:
        storefile_location = args[4]
        
        
    print("In main ", datafile_location, " ", username, " ", password, " ", storefile_location)
    # filepath_dir = datafile_location
    # customer_file_path = os.path.join(filepath_dir,"customer_small.tbl")
    # order_file_path = os.path.join(filepath_dir,"orders_small.tbl")
    # lineitem_file_path = os.path.join(filepath_dir,"lineitem_small.tbl")
    
    # print(customer_file_path)
    # print(order_file_path)
    # print(lineitem_file_path)
    # test_connection("tpch_original", username, password)

    # Setup Original Database
    setup_database_with_original_data("csci_725_tpch_original", datafile_location, username, password)
    # Setup Medium Database
    setup_database_with_medium_data("csci_725_tpch_medium", datafile_location, username, password)
    # Setup Small Database
    setup_database_with_small_data("csci_725_tpch_small", datafile_location, username, password)

    # Anomaly Databases
    anomaly_database_setup(datafile_location, username, password)

if __name__ == '__main__':
    args = sys.argv
    
    # You need to pass the full directory path to the folder containing your data file
    # You can pass the directory where you want to store the data if you would like, if not it will just create those files in current directory
    # If you are tbl files are in a folder called my_folder, pass /path/to/my_folder Eg: /home/user/my_folder
    # Sample Command to run this script: python3 database_setup.py /home/user/my_folder kavyaa mypassword /home/user/store_folder
    if len(args) < 4:
        print("Usage: pass the directory of your tbl files, username and password for your postgres")
    else:
        main(args)
