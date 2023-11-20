Toy-SQL-Engine
==============

SQL Engine implemented using Python 3. Program stores the database in files in its own format `.flodb`

## Usage

Engine supports queries very similar to SQL. All command are not case-sensitive.

### Create / Load database
To create / load database use command `load` and filename:

```
>>> LOAD cats;
```

Before loading a new database, the previous one will be saved first.

After loading the database, you will be notified about the successful loading:

```
Database has been successfully loaded.
```

or error:

```
Error: Failed to load database - *error type*.
```

Furthermore, if the file that you specify does not exist, appropriate message will appear to allow you to create the database:

```
Want to create a new database? [y for yes, n for no]: 
```

### Save database
To save current database use command `save`:

```
>>> SAVE;
```

After loading the database, you will be notified about the successful loading:

```
Database has been successfully loaded.
```

or error:

```
Error: Failed to load database - *error type*.
```

### Exit from program
To exit from program use command `exit`. Current database will be saved before closing:

```
>>> EXIT;
```

### Create table
To create table use command `create` with specified table name and column names:

```
>>> CREATE table_name (column_name [INDEXED] [,...]);
```

Engine supports column indexing to search faster.

After creating the table, appropriate message will be displayed:

```
Table *table name* has been successfully created.
```

Or error if:
* syntax is invalid
* table already exists
* specified zero columns
* column name is prohibited 

### Insert values into table
To insert values into table use command `insert` with specified table name and values:

```
>>> INSERT [INTO] table_name ("value" [,...]);
```

After inserting values into table, appropriate message will be displayed:

```
1 row has been inserted into table *table name*.
```

Or error if:
* syntax is invalid
* table not exists
* inappropriate number of columns and values
* inappropriate value type and column date type

### Select data from table
To select rows from table use command `select` with specified table:

```
>>> SELECT FROM cats;
+------+---------+------------------+
|   id | name    | favourite_food   |
+======+=========+==================+
|    1 | Murzik  | Sausages         |
+------+---------+------------------+
|    2 | Pushok  | Fish             |
+------+---------+------------------+
```

Or use filtering with multiple OR, AND:
```
>>> SELECT FROM cats WHERE name = "Murzik" OR (name > "a" AND name = "Pushok");
+------+--------+------------------+
|   id | name   | favourite_food   |
+======+========+==================+
|    1 | Murzik | Sausages         |
+------+--------+------------------+
|    2 | Pushok | Fish             |
+------+--------+------------------+
|    9 | Pushok | Fish             |
+------+--------+------------------+ 
```

Error message could be displayed if:
* syntax is invalid
* table not exists