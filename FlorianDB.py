import os
from pickle import dump, load, PickleError

from tabulate import tabulate
from collections import Counter

from AVLTree import AVLTree

# actually not used
from colorama import Fore, Style


class FlorianDB:
    def __init__(self):
        """
        Initialize database

        filename: name of the file where stored or will be stored data of database, defaults to None

        All our data will be stored in variable self.db. It will look like:
        self.db (dict) = {
            <name of the table> (dict): {
                'col_names' (list): List of column names of the table
                'data_types' (list): List of data type for each column
                'data' (list): List of the rows that was inserted into the table

                # then will be stored
                <1st indexed column name> (AVLTree): Tree of unique values of appropriate column
                ...
                # and so on for all indexed columns
            }
            ...
        }
        """

        self.db = {}
        self.filename = ''

    def load(self, filename):
        if not filename.endswith('.flodb'):
            filename += '.flodb'

        # save previous database
        if self.filename:
            self.save()

        if os.path.isfile(filename):
            try:
                with open(filename, 'rb') as f:
                    self.db = load(f)

                self.filename = filename

                print('Database has been successfully loaded.\n')
                return True

            except (EOFError, FileNotFoundError, PickleError) as e:
                print(f'Error: Failed to load database - {e}.\n')
                return False

        ans = input('Want to create a new database? [y for yes, n for no]: ')
        while ans.lower() not in ['y', 'n']:
            print('\nInvalid input. Please enter either "y" for yes or "n" for no.')
            ans = input('Want to create a new database? [y for yes, n for no]: ')
        print()

        if ans.lower() == 'y':
            self.filename = filename
            self.db = {}
            self.save()
            return True
        else:
            return False

    def save(self):
        if not self.filename:
            return False

        try:
            with open(self.filename, 'wb') as f:
                dump(self.db, f)

            print('Database has been successfully saved.\n')
            return True

        except PickleError as e:
            print(f'Error: Failed to save database - {e}.\n')
            return False

    def is_table_exist(self, name):
        return True if name in self.db else False

    @staticmethod
    def is_column_exist(table, column_name):
        return True if column_name in table['col_names'] else False

    @staticmethod
    def is_indexed(table, column_name):
        return True if column_name in table else False

    def create_table(self, name: str, cols: list, indexed: list):
        # check whether the table exists
        if self.is_table_exist(name):
            print(f'Error: Table {name} already exists.\n')
            return False

        if not cols:
            print('Error: Table must have at least one column.\n')
            return False

        # check whether any of entered column names are prohibited
        if any(['col_names', 'data_types', 'data']) in cols:
            print(f'Error: Names \'col_names\', \'data_types\', \'data\' are prohibited to use for column names.\n')
            return False

        self.db[name] = {
            'col_names': cols,
            'data_types': [],
            'data': []
        }

        if indexed:
            for el in indexed:
                self.db[name][el] = AVLTree()

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

        for in_col in self.db[name]:
            if in_col in ['col_names', 'data_types', 'data']:
                continue

            column_index = self.db[name]['col_names'].index(in_col)
            if isinstance(values[column_index], int):
                self.db[name][in_col].insert_or_update_node(values[column_index], values)
            else:
                self.db[name][in_col].insert_or_update_node(values[column_index].lower(), values)

        print(f'1 row has been inserted into table {name}.\n')
        return True

    def select(self, name: str, conds: list):
        # check whether the table exists
        if not self.is_table_exist(name):
            print(f'Error: Table {name} doesn\'t exists.\n')
            return False

        # check if there is WHERE expression
        if not conds:
            self.print_table(self.db[name])
            return True

        res_rows = self._select(self.db[name], conds)

        # if error raised
        if res_rows is False:
            return False

        # display table
        self.print_table(self.db[name], res_rows)
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

            common = list((Counter(l_tuple) | Counter(r_tuple)).elements())

            return common

        elif op == 'AND':
            l_tuple = map(tuple, l_op)
            r_tuple = map(tuple, r_op)

            combined = list((Counter(l_tuple) & Counter(r_tuple)).elements())

            return combined

        else:
            # check whether the entered column exists
            if not self.is_column_exist(table, l_op):
                print('Invalid syntax: one of the operands in condition must be the column name.\n')
                return False

            operator_functions = {
                '=': lambda x, y: x == y,
                '<': lambda x, y: x < y,
                '>': lambda x, y: x > y
            }

            try:
                compare_func = operator_functions[op]
            except KeyError:
                print(f'Error: Invalid operator {op}!\n')
                return False

            if isinstance(r_op, str):
                r_op = r_op.lower()

            if self.is_indexed(table, l_op):
                if op == '=':
                    return table[l_op].get_equal(r_op)
                elif op == '<':
                    return table[l_op].get_values_less_than(r_op)
                elif op == '>':
                    return table[l_op].get_values_greater_than(r_op)

            else:
                col_id = table['col_names'].index(l_op)
                result = []

                if isinstance(r_op, str):
                    for row in table['data']:
                        if compare_func(row[col_id].lower(), r_op):
                            result.append(row)
                else:
                    for row in table['data']:
                        if compare_func(row[col_id], r_op):
                            result.append(row)

                return result

    @staticmethod
    def print_table(table: dict, data=None):
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
        # for key, value in result.items():
        #     print(key, ": ", value)
        # -------------------------------

        command = result['command'].upper()

        if self.db.filename == '' and command not in ["LOAD", "EXIT"]:
            print('Error: Load database first!\n')
            return

        if command == "CREATE":
            table_name = result['table_name']
            col_names = result['col_names']
            indexed_cols = result['indexed_cols']

            self.db.create_table(table_name, col_names, indexed_cols)

        elif command == "INSERT":
            table_name = result['table_name']
            col_values = result['col_values']

            self.db.insert(table_name, col_values)

        elif command == "SELECT":
            table_name = result['table_name']
            conditions = result['conditions']

            self.db.select(table_name, conditions)

        elif command == "LOAD":
            filename = result['filename']

            self.db.load(filename)

        elif command == "SAVE":
            self.db.save()

        else:
            self.db.save()
            exit(0)
