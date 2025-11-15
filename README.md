**Steps to run**

1. Navigate to main directory
2. add auth.py with function to get mongo connection string ("getConnectionString()")
3. run main.py
   
**functions**
- add_anomalies
  - Artificially add anomalies into the data
- detect_anomalies
  - Runs the negative selection algorithm to find anomalies
- load_data
  - Load data into the program to start
- load_initial_data
  - Load the initial data
- save_data
  - Saves the initial state of the data before anomalies
- quit 
  - Exits the program

**about data**
We need to first setup the database with original data. This is our database with largest size. We then also sample data and get small(1% of original) and medium(10% of original) databases. Once you setup postgresql on your machine, run the following commands.

Step 1: Create the Original database and give all privilidges to your user
CREATE database tpch_original;
GRANT ALL PRIVILEGES ON tpch_original TO your_user;

Step 2: Connect to your database and create the required tables (Please note we got DDL commands from the benchmark)
In your terminal run: psql -d tpch_original -U your_user
Inside the shell run DDL commands present on DDL file on repo

Step 3: Copy the data to your database. (We took the tbl files from the benchmark and had to remove the last "|" value. After cleaning it we ran the copy commands. The cleaned files are uploaded on the repo.)
Inside your psql shell connected to tpch_original DB, run: 
1. \copy customer FROM '/path/to/file/customer.tbl' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);
2. \copy orders FROM '/path/to/file/orders.tbl' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);
3. \copy lineitem FROM '/path/to/file/lineitem.tbl' WITH (FORMAT csv, DELIMITER '|', NULL '', HEADER false);

Step 4: Create tbl files for small and medium db. We do this by first creating tempory tables and then dumping that data in tbl files. We need to make sure that we randomly sample lineitem and then get all the associated orders and customer lines.
1. CREATE TABLE lineitem_small AS SELECT * FROM lineitem WHERE random() < 0.01;
2. CREATE TABLE orders_small AS SELECT * FROM orders WHERE o_orderkey IN (SELECT l_orderkey FROM lineitem_small);
3. CREATE TABLE customer_small AS SELECT * FROM customer WHERE c_custkey IN (SELECT o_custkey FROM orders_small);
4. \copy (SELECT * FROM customer_small) TO '/path/to/file/customer_small.tbl' WITH (FORMAT csv, DELIMITER '|', HEADER false);
5. \copy (SELECT * FROM orders_small) TO '/home/kavyaa/RIT_Academics/Fall2025/NoSQL_NewSQL/Project/orders_small.tbl' WITH (FORMAT csv, DELIMITER '|', HEADER false);
6. \copy (SELECT * FROM lineitem_small) TO '/home/kavyaa/RIT_Academics/Fall2025/NoSQL_NewSQL/Project/lineitem_small.tbl' WITH (FORMAT csv, DELIMITER '|', HEADER false);
7. CREATE TABLE lineitem_medium AS SELECT * FROM lineitem WHERE random() < 0.1;
8. CREATE TABLE orders_medium AS SELECT * FROM orders WHERE o_orderkey IN (SELECT l_orderkey FROM lineitem_medium);
9. CREATE TABLE customer_medium AS SELECT * FROM customer WHERE c_custkey IN (SELECT o_custkey FROM orders_medium);
10. \copy (SELECT * FROM customer_medium) TO '/home/kavyaa/RIT_Academics/Fall2025/NoSQL_NewSQL/Project/customer_medium.tbl' WITH (FORMAT csv, DELIMITER '|', HEADER false);
11. \copy (SELECT * FROM orders_medium) TO '/home/kavyaa/RIT_Academics/Fall2025/NoSQL_NewSQL/Project/orders_medium.tbl' WITH (FORMAT csv, DELIMITER '|', HEADER false);
12. \copy (SELECT * FROM lineitem_medium) TO '/home/kavyaa/RIT_Academics/Fall2025/NoSQL_NewSQL/Project/lineitem_medium.tbl' WITH (FORMAT csv, DELIMITER '|', HEADER false);
13. drop table orders_small, orders_medium, lineitem_medium, lineitem_small, customer_small, customer_medium;

Step 5: Create tpch small and medium databases. (postgres shell)
CREATE database tpch_small;
GRANT ALL PRIVILEGES ON tpch_small TO your_user;
CREATE database tpch_medium;
GRANT ALL PRIVILEGES ON tpch_medium TO your_user;

Step 6: Repeat Step 2 on these 2 databases
Step 7: Repeat Step 3 but with appropriate .tbl files we created in step 4 and appropriate db shell.
