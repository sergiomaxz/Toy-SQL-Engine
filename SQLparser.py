import lexer
from typing import Union

P_OPEN = '('
P_CLOSE = ')'


class Parser:
    def __init__(self, plexer: lexer.Lexer):
        self.lexer = plexer
        self._curr_token = self.lexer.get_next_token()

    def eat(self):
        self._curr_token = self.lexer.get_next_token()

    def _error_select(self, instead) -> dict:
        if self._curr_token.ttype == 'EOF':
            return {'success': False,
                    'error': f'Invalid syntax: Unexpected {self._curr_token.ttype} instead {instead} while parsing.\n'
                             f'Correct syntax: SELECT FROM table_name [WHERE condition]\n'
                             f'\t\t\t\tcondition := column_name operator "value" | (condition) AND (condition) | (condition) OR (condition)\n'
                             f'\t\t\t\toperator := ( = | < | > )\n'}

        return {'success': False,
                'error': f'Invalid syntax: Unexpected {self._curr_token.ttype}:"{self._curr_token.value}" instead {instead} while parsing.\n'
                         f'Correct syntax: SELECT FROM table_name [WHERE condition]\n'
                         f'\t\t\t\tcondition := column_name operator "value" | (condition) AND (condition) | (condition) OR (condition)\n'
                         f'\t\t\t\toperator := ( = | < | > )\n'}

    def _error_insert(self, instead) -> dict:
        if self._curr_token.ttype == 'EOF':
            return {'success': False,
                    'error': f'Invalid syntax: Unexpected {self._curr_token.ttype} instead {instead} while parsing.\n'
                             f'Correct syntax: INSERT [INTO] table_name ("value" [,...])\n'}

        return {'success': False,
                'error': f'Invalid syntax: Unexpected {self._curr_token.ttype}:"{self._curr_token.value}" instead {instead} while parsing.\n'
                         f'Correct syntax: INSERT [INTO] table_name ("value" [,...])\n'}

    def _error_create(self, instead) -> dict:
        if self._curr_token.ttype == 'EOF':
            return {'success': False,
                    'error': f'Invalid syntax: Unexpected {self._curr_token.ttype} instead {instead} while parsing.\n'
                             f'Correct syntax: CREATE table_name (column_name [INDEXED] [,...])\n'}

        return {'success': False,
                'error': f'Invalid syntax: Unexpected {self._curr_token.ttype}:"{self._curr_token.value}" instead {instead} while parsing.\n'
                         f'Correct syntax: CREATE table_name (column_name [INDEXED] [,...])\n'}

    def parse_create(self) -> dict:
        """
        Parse the sql create query that insert row into the table

        :return: dict(
            'success' (bool): Whether query syntax is valid
            'command' (str): Function name
            'table_name' (str): Table name
            'col_names' (list): List of column names
            'indexed_cols' (list): List of columns that need to be indexed
        )

        If query syntax is invalid:
        :return: dict(
            'success' (bool): False
            'error' (str): Error type and description
        )
        """

        result = {
            'success': True,
            'command': self._curr_token.value,
            'table_name': '',
            'col_names': [],
            'indexed_cols': []
        }
        self.eat()

        if self._curr_token.ttype != lexer.IDENTIFIER:
            if self._curr_token.ttype == lexer.KEYWORD:
                return {'success': False,
                        'error': f'Name error: Forbidden to use reserved words as table names.\n'}
            return self._error_create('<table name>')

        result['table_name'] = self._curr_token.value
        self.eat()

        if (self._curr_token.ttype, self._curr_token.value) != (lexer.PARENTHESES, P_OPEN):
            return self._error_create(f'"{P_OPEN}"')
        self.eat()

        col_names = []
        indexed_cols = []

        while self._curr_token.value != P_CLOSE:
            if self._curr_token.ttype != lexer.IDENTIFIER:
                if self._curr_token.ttype == lexer.KEYWORD:
                    return {'success': False,
                            'error': f'Name error: Forbidden to use reserved words as column names.\n'}
                return self._error_create('<column name>')

            col_names.append(self._curr_token.value)
            self.eat()

            if self._curr_token.value.upper() == 'INDEXED':
                indexed_cols.append(col_names[-1])
                self.eat()

            if self._curr_token.value not in [',', P_CLOSE]:
                if self._curr_token.ttype == 'EOF':
                    return self._error_create(f'"{P_CLOSE}"')
                return {'success': False,
                        'error': f'Column names error: Column name can have only one property: INDEXED.\n'}

            if self._curr_token.value != P_CLOSE:
                self.eat()

            if self._curr_token.ttype == 'EOF':
                return self._error_create(f'"{P_CLOSE}"')

        self.eat()
        if self._curr_token.ttype != 'EOF':
            return self._error_create('EOF')

        result['col_names'] = col_names
        result['indexed_cols'] = indexed_cols
        return result

    def parse_insert(self) -> dict:
        """
        Parse the sql insert query that insert row into the table

        :return: dict(
            'success' (bool): Whether query syntax is valid
            'command' (str): Function name
            'table_name' (str): Table name
            'col_values' (list): List of values that will be inserted to table
        )

        If query syntax is invalid:
        :return: dict(
            'success' (bool): False
            'error' (str): Error type and description
        )
        """

        result = {
            'success': True,
            'command': self._curr_token.value,
            'table_name': '',
            'col_values': []
        }
        self.eat()

        if self._curr_token.value.upper() == 'INTO':
            self.eat()

        if self._curr_token.ttype != lexer.IDENTIFIER:
            if self._curr_token.ttype == lexer.KEYWORD:
                return {'success': False,
                        'error': f'Name error: Forbidden to use reserved words as table names.\n'}
            return self._error_insert('<table name>')

        result['table_name'] = self._curr_token.value
        self.eat()

        if (self._curr_token.ttype, self._curr_token.value) != (lexer.PARENTHESES, P_OPEN):
            return self._error_insert(f'"{P_OPEN}"')
        self.eat()

        col_values = []

        while self._curr_token.value != P_CLOSE:
            if self._curr_token.ttype not in (lexer.QUOTES, lexer.NUMBER):
                if self._curr_token.ttype == lexer.KEYWORD:
                    return {'success': False,
                            'error': f'Name error: Forbidden to use reserved words as column names.\n'}
                return self._error_insert('<column name>')

            col_values.append(self._curr_token.value)
            self.eat()

            if self._curr_token.value not in [',', P_CLOSE]:
                if self._curr_token.ttype == 'EOF':
                    return self._error_insert(f'"{P_CLOSE}"')
                return {'success': False,
                        'error': f'Column names error: Column name can have only one property: INDEXED.\n'}

            if self._curr_token.value != P_CLOSE:
                self.eat()

            if self._curr_token.ttype == 'EOF':
                return self._error_insert(f'"{P_CLOSE}"')

        self.eat()
        if self._curr_token.ttype != 'EOF':
            return self._error_insert('EOF')

        result['col_values'] = col_values
        return result

    def parse_select(self) -> dict:
        """
        Parse the sql select query that select rows from the table

        :return: dict(
            'success' (bool): Whether query syntax is valid
            'command' (str): Function name
            'table_name' (str): Table name
            'conditions' (list): List of WHERE clause conditions by which records should be filtered
        )

        If query syntax is invalid:
        :return: dict(
            'success' (bool): False
            'error' (str): Error type and description
        )
        """

        result = {
            'success': True,
            'command': self._curr_token.value,
            'table_name': '',
            'conditions': []
        }
        self.eat()

        if self._curr_token.value.upper() != 'FROM':
            return self._error_select('FROM')
        self.eat()

        if self._curr_token.ttype != lexer.IDENTIFIER:
            if self._curr_token.ttype == lexer.KEYWORD:
                return {'success': False,
                        'error': f'Name error: Forbidden to use reserved words as table names.\n'}
            return self._error_select('<table name>')

        result['table_name'] = self._curr_token.value
        self.eat()

        if self._curr_token.ttype == 'EOF':
            return result

        if self._curr_token.value.upper() != 'WHERE':
            return self._error_select('WHERE')
        self.eat()

        conditions = self.expr()

        if type(conditions) is dict:
            return conditions

        result['conditions'] = conditions

        return result

    def expr(self) -> Union[list, dict]:
        result = self.term()

        if type(result) is dict:
            return result

        while self._curr_token.ttype == lexer.KEYWORD and self._curr_token.value.upper() in ('OR', 'AND'):
            result = [result, self._curr_token.value]
            self.eat()

            if self._curr_token.ttype not in (lexer.IDENTIFIER, lexer.PARENTHESES):
                return self._error_select(f'"{P_OPEN}" | column_name')

            tmp_token = self.term()
            if type(tmp_token) is dict:
                return tmp_token

            result.append(tmp_token)

        return result

    def term(self) -> Union[list, dict]:
        result = self.factor()

        if type(result) is dict:
            return result

        while self._curr_token.ttype == lexer.OPERATOR:
            result = [result, self._curr_token.value]
            self.eat()

            if self._curr_token.ttype not in (lexer.QUOTES, lexer.NUMBER):
                return self._error_select('"value"')
            result.append(self.factor())

        if type(result) is not list:
            return self._error_select('operator')

        return result

    def factor(self) -> Union[list, str, int, dict]:
        token = self._curr_token
        if (token.ttype, token.value) == (lexer.PARENTHESES, P_OPEN):
            self.eat()
            res = self.expr()

            if type(res) is dict:
                return res

            if (self._curr_token.ttype, self._curr_token.value) != (lexer.PARENTHESES, P_CLOSE):
                return self._error_select(f'"{P_CLOSE}"')

            self.eat()
            return res

        elif token.ttype in (lexer.IDENTIFIER, lexer.NUMBER, lexer.QUOTES):
            self.eat()
            return token.value

        else:
            return self._error_select('column_name | "value"')

    def parse(self) -> dict:
        if self._curr_token.value.upper() == 'CREATE':
            return self.parse_create()

        if self._curr_token.value.upper() == 'INSERT':
            return self.parse_insert()

        if self._curr_token.value.upper() == 'SELECT':
            return self.parse_select()

        return {'success': False, 'error': 'Error: Unknown command.\n'}
