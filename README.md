**To create database automatically**
1. Download the original data [here](https://drive.google.com/drive/folders/1nTfZMklwk2XcOB9Tyk4MduWzKk1CgXH-?usp=sharing). 
2. Run the database_setup.py file with arguments for data_location, PostgreSQL username, and password. 
   1. More info below to run manually

**functions**
- detect_anomalies
  - Runs the negative selection algorithm to find anomalies
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

Step 3: Copy the data to your database. (We took the tbl files from the benchmark and had to remove the last "|" value. After cleaning it we ran the copy commands. The cleaned files are uploaded [here](https://drive.google.com/drive/folders/1nTfZMklwk2XcOB9Tyk4MduWzKk1CgXH-?usp=sharing).)
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

**Introducing Anomalies into the Data**
A detailed explanation of each anomaly is provided in the report. Following steps just outline how to do the datasetup for it.
- **Missing Record Anomalies:** randomly deleted 5%, 10%, 20%, and 50% of the records from all three tables.
   - Step 1: Create a copy of the original database
   - Step 2: Randomly delete records. Note we don't care if some record in data references value that is deleted. Run the following commands to delete the data randomly.
      - delete from customer where random() <= 0.05; -- This randomly deletes 5% of records from customer table. Change 0.05 to 0.1 to get 10%, 0.2 to get 20% and 0.5 to 50%
      - delete from orders where random() <= 0.05; -- This randomly deletes 5% of records from customer table. Change 0.05 to 0.1 to get 10%, 0.2 to get 20% and 0.5 to 50%
      - delete from lineitem where random() <= 0.05; -- This randomly deletes 5% of records from customer table. Change 0.05 to 0.1 to get 10%, 0.2 to get 20% and 0.5 to 50%
   - Step 3: Do Steps 1 and 2 to get 10%, 20%, and 50% missing record anomaly.
   - Step 4: Repeat Steps 1 through 3 with small and medium size dataset.
- **Value Anomalies**
   - Step 1: Create a copy of original database
   - Step 2: We identified the numeric value columns we want to introduce this anomaly to. We didn't introduce anomaly to id columns. Following is the commands to introduce this anomaly in the data.
      -  UPDATE customer SET c_nationkey = CEIL(c_nationkey * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE customer SET c_acctbal = (c_acctbal * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE orders SET o_totalprice = (o_totalprice * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE orders SET o_shippriority = CEIL(o_shippriority * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE lineitem SET l_linenumber = CEIL(l_linenumber * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE lineitem SET l_quantity = (l_quantity * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE lineitem SET l_extendedprice = (l_extendedprice * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE lineitem SET l_discount = (l_discount * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
      -  UPDATE lineitem SET l_tax = (l_tax * (CASE WHEN random() < 0.5 THEN 1 + (0.05 + (random() * 0.05)) ELSE 1 - (0.05 + (random() * 0.05)) END)) WHERE random() < 0.20;
   - Step 3: Repeat Steps 1 and 2 with small and medium size dataset.
- **Outlier Anomalies**
   - Step 1: Create a copy of original database
   - Step 2: Run the following commands:
      - UPDATE orders SET o_totalprice = 100*o_totalprice WHERE random() < 0.2;
      - UPDATE lineitem SET l_tax = 100*l_tax WHERE random() < 0.2;
      - UPDATE lineitem SET l_extendedprice = 100*l_extendedprice WHERE random() < 0.2;
   - Step 3: Repeat Steps 1 and 2 with small and medium size dataset.
- **Date Anomalies**
   - Step 1: Create a copy of original database
   - Step 2: Run the following command:
      - UPDATE lineitem SET l_shipdate = '1998-01-01', l_receiptdate = '1996-01-05' WHERE random() < 0.20;
   - Step 3: Repeat Steps 1 and 2 with small and medium size dataset.
