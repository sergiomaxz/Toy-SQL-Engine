import json
import os
from tabulate import tabulate
from collections import Counter


class FlorianDB:
    def __init__(self, filename=None):
        """
        Initialize database

        :param filename: name of the file where stored or will be stored data of database, defaults to None
        :type filename: str

        All our data will be stored in argument self.db. It will look like:
        self.db = {
            <name of the table> (dict): {
                'col_names' (list): List of column names of the table
                'data_types' (list): List of data type for each column
                'data' (list): List of the rows that was inserted into the table

                # then will be stored
                <1st indexed column name> (dict): {
                    <1st unique value> (list): List of rows with this value in the appropriate column
                    ...
                }
                ...
                # and so on for all indexed columns
            }
            ...
        }
        """

        # self.db = {
        #     'name': {
        #         'col_names': [],
        #         'data_types': [],
        #         'data': [],
        #         'my_fav_food': []
        #     }
        # }

        self.db = {}

        self.filename = filename

    def load(self):
        if os.path.isfile(self.filename):
            self.db = json.load(open(self.filename, 'r'))
        else:
            self.db = {}

    def save(self):
        try:
            json.dump(self.db, open(self.filename, 'w+'))
            return True
        except:
            return False

    def is_table_exist(self, name):
        return True if name in self.db else False

    @staticmethod
    def is_column_exist(table, column_name):
        return True if column_name in table['col_names'] else False

    def create_table(self, name: str, cols: list, indexed: list):
        # check whether the table exists
        if self.is_table_exist(name):
            print(f'Error: Table {name} already exists.\n')
            return False

        # check whether any of entered column names are prohibited
        if any(['col_names', 'data_type', 'data']) in cols:
            print(f'Error: Names \'col_names\', \'data_types\', \'data\' are prohibited to use for column names.\n')
            return False

        self.db[name] = {
            'col_names': cols,
            'data_types': [],
            'data': []
        }

        if indexed:
            for el in indexed:
                self.db[name][el] = dict()

        print(f'Table {name} has been successfully created.\n')
        return True

    def insert(self, name: str, values: list):
        # check whether the table exists
        if not self.is_table_exist(name):
            print(f'Error: Table {name} doesn\'t exists.\n')
            return False

        # check whether the number of columns and the number of entered values matches
        if len(self.db[name]['col_names']) != len(values):
            print("Error: Column count doesn't match value count.\n")
            return False

        if not self.db[name]['data_types']:
            self.db[name]['data_types'] = [type(value) for value in values]

        # check whether the table data type and the entered data type matches
        for ctype, value in zip(self.db[name]['data_types'], values):
            if not isinstance(value, ctype):
                print(f'Error: Value {value} doesn\'t match type {str(ctype)[7:-1]}.\n')
                return False

        self.db[name]['data'].append(values)

        print(f'1 row has been inserted into table {name}.\n')
        return True

    def select(self, name: str, conds: list):
        # check whether the table exists
        if not self.is_table_exist(name):
            print(f'Error: Table {name} doesn\'t exists.\n')
            return False

        # check if there is WHERE expression
        if not conds:
            self.repr(self.db[name])
            return True

        res_rows = self._select(self.db[name], conds)

        # if error raised
        if res_rows is False:
            return False

        # display table
        self.repr(self.db[name], res_rows)
        return True

    def _select(self, table: dict, conds: list):
        if isinstance(conds[0], list):
            left_op = self._select(table, conds[0])
            right_op = self._select(table, conds[2])
            oper = conds[1]

            # if error raised
            if left_op is False or right_op is False:
                return False

            return self._filter(oper, left_op, right_op)

        left_op, oper, right_op = conds
        return self._filter(oper, left_op, right_op, table)

    def _filter(self, op, l_op, r_op, table=None):
        if op == 'OR':
            l_tuple = map(tuple, l_op)
            r_tuple = map(tuple, r_op)

            # common = list(map(list, set(l_tuple).union(set(r_tuple))))
            common = list((Counter(l_tuple) | Counter(r_tuple)).elements())

            return common

        elif op == 'AND':
            l_tuple = map(tuple, l_op)
            r_tuple = map(tuple, r_op)

            # combined = list(map(list, set(l_tuple).intersection(set(r_tuple))))
            combined = list((Counter(l_tuple) & Counter(r_tuple)).elements())

            return combined

        elif op == '=':
            # check whether the entered column exists
            if not self.is_column_exist(table, l_op):
                print('Invalid syntax: one of the operands in condition must be the column name.\n')
                return False

            col_id = table['col_names'].index(l_op)
            result = []

            # check whether the value is integer
            if isinstance(r_op, int):
                for row in table['data']:
                    if row[col_id] == r_op:
                        result.append(row)

            else:
                r_op_lower = r_op.lower()
                for row in table['data']:
                    if row[col_id].lower() == r_op_lower:
                        result.append(row)

            return result

        elif op == '<':
            # check whether the entered column exists
            if not self.is_column_exist(table, l_op):
                print('Invalid syntax: one of the operands in condition must be the column name.\n')
                return False

            col_id = table['col_names'].index(l_op)
            result = []

            # check whether the value is integer
            if isinstance(r_op, int):
                for row in table['data']:
                    if row[col_id] < r_op:
                        result.append(row)

            else:
                r_op_lower = r_op.lower()
                for row in table['data']:
                    if row[col_id].lower() < r_op_lower:
                        result.append(row)

            return result

        else:
            # check whether the entered column exists
            if not self.is_column_exist(table, l_op):
                print('Invalid syntax: one of the operands in condition must be the column name.\n')
                return False

            col_id = table['col_names'].index(l_op)
            result = []

            # check whether the value is integer
            if isinstance(r_op, int):
                for row in table['data']:
                    if row[col_id] > r_op:
                        result.append(row)

            else:
                r_op_lower = r_op.lower()
                for row in table['data']:
                    if row[col_id].lower() > r_op_lower:
                        result.append(row)

            return result

    def repr(self, table: dict, data=None):
        col_names = table['col_names']

        if data is None:
            data = table['data']

        # Create a table with column headers and data
        table = [col_names] + data

        # Using tabulate for table formatting and output
        print(tabulate(table, headers='firstrow', tablefmt='grid'), '\n')

class Interpreter:
    def __init__(self, db: FlorianDB, parser):
        self.db = db
        self.parser = parser

    def interpret(self):
        result = self.parser.parse()

        if not result['success']:
            print(result['error'])
            return

        # debug -------------------------
        for key, value in result.items():
            print(key, ": ", value)
        # -------------------------------

        command = result['command'].upper()

        if command == "CREATE":
            table_name = result['table_name']
            col_names = result['col_names']
            indexed_cols = result['indexed_cols']

            self.db.create_table(table_name, col_names, indexed_cols)

        elif command == "INSERT":
            table_name = result['table_name']
            col_values = result['col_values']

            self.db.insert(table_name, col_values)

        else:
            table_name = result['table_name']
            conditions = result['conditions']

            self.db.select(table_name, conditions)
