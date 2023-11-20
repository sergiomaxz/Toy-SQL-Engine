import lexer
from typing import Union

P_OPEN = '('
P_CLOSE = ')'


class Parser:
    def __init__(self, plexer: lexer.Lexer):
        self.lexer = plexer
        self._curr_token = self.lexer.get_next_token()

    def advance_to_next_token(self):
        self._curr_token = self.lexer.get_next_token()

    def _error_select(self, instead) -> dict:
        unexpected = f'{self._curr_token.ttype}' if self._curr_token.ttype == 'EOF' else f'{self._curr_token.ttype}:"{self._curr_token.value}"'

        return {'success': False,
                'error': f'Invalid syntax: Unexpected {unexpected} instead {instead} while parsing.\n'
                         f'Correct syntax: SELECT FROM table_name [WHERE condition]\n'
                         f'\t\t\t\tcondition := column_name operator "value" | (condition) AND (condition) | (condition) OR (condition)\n'
                         f'\t\t\t\toperator := ( = | < | > )\n'}

    def _error_insert(self, instead) -> dict:
        unexpected = f'{self._curr_token.ttype}' if self._curr_token.ttype == 'EOF' else f'{self._curr_token.ttype}:"{self._curr_token.value}"'

        return {'success': False,
                'error': f'Invalid syntax: Unexpected {unexpected} instead {instead} while parsing.\n'
                         f'Correct syntax: INSERT [INTO] table_name ("value" [,...])\n'}

    def _error_create(self, instead) -> dict:
        unexpected = f'{self._curr_token.ttype}' if self._curr_token.ttype == 'EOF' else f'{self._curr_token.ttype}:"{self._curr_token.value}"'

        return {'success': False,
                'error': f'Invalid syntax: Unexpected {unexpected} instead {instead} while parsing.\n'
                         f'Correct syntax: CREATE table_name (column_name [INDEXED] [,...])\n'}

    def parse_create(self) -> dict:
        """
        Parse the sql create query that create table in the database

        :return: dict(
            'success' (bool): Whether query syntax is valid
            'command' (str): Command name
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
        self.advance_to_next_token()

        if self._curr_token.ttype != lexer.IDENTIFIER:
            if self._curr_token.ttype == lexer.KEYWORD:
                return {'success': False,
                        'error': f'Name error: Forbidden to use reserved words as table names.\n'}
            return self._error_create('<table name>')

        result['table_name'] = self._curr_token.value
        self.advance_to_next_token()

        if (self._curr_token.ttype, self._curr_token.value) != (lexer.PARENTHESES, P_OPEN):
            return self._error_create(f'"{P_OPEN}"')
        self.advance_to_next_token()

        col_names = []
        indexed_cols = []

        while self._curr_token.value != P_CLOSE:
            if self._curr_token.ttype != lexer.IDENTIFIER:
                if self._curr_token.ttype == lexer.KEYWORD:
                    return {'success': False,
                            'error': f'Name error: Forbidden to use reserved words as column names.\n'}
                return self._error_create('<column name>')

            col_names.append(self._curr_token.value)
            self.advance_to_next_token()

            if isinstance(self._curr_token.value, str) and self._curr_token.value.upper() == 'INDEXED':
                indexed_cols.append(col_names[-1])
                self.advance_to_next_token()

            if self._curr_token.value not in [',', P_CLOSE]:
                if self._curr_token.ttype == 'EOF':
                    return self._error_create(f'"{P_CLOSE}"')
                return {'success': False,
                        'error': f'Column names error: Column name can have only one property: INDEXED.\n'}

            if self._curr_token.value != P_CLOSE:
                self.advance_to_next_token()

            if self._curr_token.ttype == 'EOF':
                return self._error_create(f'"{P_CLOSE}"')

        self.advance_to_next_token()
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
            'command' (str): Command name
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
        self.advance_to_next_token()

        if isinstance(self._curr_token.value, str) and self._curr_token.value.upper() == 'INTO':
            self.advance_to_next_token()

        if self._curr_token.ttype != lexer.IDENTIFIER:
            if self._curr_token.ttype == lexer.KEYWORD:
                return {'success': False,
                        'error': f'Name error: Forbidden to use reserved words as table names.\n'}
            return self._error_insert('<table name>')

        result['table_name'] = self._curr_token.value
        self.advance_to_next_token()

        if (self._curr_token.ttype, self._curr_token.value) != (lexer.PARENTHESES, P_OPEN):
            return self._error_insert(f'"{P_OPEN}"')
        self.advance_to_next_token()

        col_values = []

        while self._curr_token.value != P_CLOSE:
            if self._curr_token.ttype not in (lexer.QUOTES, lexer.NUMBER):
                if self._curr_token.ttype == lexer.KEYWORD:
                    return {'success': False,
                            'error': f'Name error: Forbidden to use reserved words as column names.\n'}
                return self._error_insert('<column name>')

            col_values.append(self._curr_token.value)
            self.advance_to_next_token()

            if self._curr_token.value not in [',', P_CLOSE]:
                if self._curr_token.ttype == 'EOF':
                    return self._error_insert(f'"{P_CLOSE}"')
                return {'success': False,
                        'error': f'Column names error: Column name can have only one property: INDEXED.\n'}

            if self._curr_token.value != P_CLOSE:
                self.advance_to_next_token()

            if self._curr_token.ttype == 'EOF':
                return self._error_insert(f'"{P_CLOSE}"')

        self.advance_to_next_token()
        if self._curr_token.ttype != 'EOF':
            return self._error_insert('EOF')

        result['col_values'] = col_values
        return result

    def parse_select(self) -> dict:
        """
        Parse the sql select query that select rows from the table

        :return: dict(
            'success' (bool): Whether query syntax is valid
            'command' (str): Command name
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
        self.advance_to_next_token()

        if not isinstance(self._curr_token.value, str) or self._curr_token.value.upper() != 'FROM':
            return self._error_select('FROM')
        self.advance_to_next_token()

        if self._curr_token.ttype != lexer.IDENTIFIER:
            if self._curr_token.ttype == lexer.KEYWORD:
                return {'success': False,
                        'error': f'Name error: Forbidden to use reserved words as table names.\n'}
            return self._error_select('<table name>')

        result['table_name'] = self._curr_token.value
        self.advance_to_next_token()

        if self._curr_token.ttype == 'EOF':
            return result

        if not isinstance(self._curr_token.value, str) or self._curr_token.value.upper() != 'WHERE':
            return self._error_select('WHERE')
        self.advance_to_next_token()

        conditions = self.expr()

        if isinstance(conditions, dict):
            return conditions

        result['conditions'] = conditions

        if self._curr_token.ttype != 'EOF':
            return self._error_select('OR | AND')

        return result

    def expr(self) -> Union[list, dict]:
        """ expr: term [(OR | AND) term]* """

        result = self.term()

        if isinstance(result, dict):
            return result

        while self._curr_token.ttype == lexer.KEYWORD and self._curr_token.value.upper() in ('OR', 'AND'):
            result = [result, self._curr_token.value]
            self.advance_to_next_token()

            if self._curr_token.ttype not in (lexer.IDENTIFIER, lexer.PARENTHESES):
                return self._error_select(f'"{P_OPEN}" | column_name')

            tmp_token = self.term()
            if isinstance(tmp_token, dict):
                return tmp_token

            result.append(tmp_token)

        return result

    def term(self) -> Union[list, dict]:
        """ term: factor ((= | > | <) factor)* """

        result = self.factor()

        if isinstance(result, dict):
            return result

        while self._curr_token.ttype == lexer.OPERATOR:
            result = [result, self._curr_token.value]
            self.advance_to_next_token()

            if self._curr_token.ttype not in (lexer.QUOTES, lexer.NUMBER):
                return self._error_select('"value"')
            result.append(self.factor())

        if not isinstance(result, list):
            return self._error_select('operator')

        return result

    def factor(self) -> Union[list, str, int, dict]:
        """ factor: (IDENTIFIER | QUOTES | NUMBER) | LPAREN expr RPAREN """

        token = self._curr_token
        if (token.ttype, token.value) == (lexer.PARENTHESES, P_OPEN):
            self.advance_to_next_token()
            res = self.expr()

            if isinstance(res, dict):
                return res

            if (self._curr_token.ttype, self._curr_token.value) != (lexer.PARENTHESES, P_CLOSE):
                return self._error_select(f'"{P_CLOSE}"')

            self.advance_to_next_token()
            return res

        elif token.ttype in (lexer.IDENTIFIER, lexer.NUMBER, lexer.QUOTES):
            self.advance_to_next_token()
            return token.value

        else:
            return self._error_select('column_name | "value"')

    def parse_load(self) -> dict:
        result = {
            'success': True,
            'command': self._curr_token.value,
        }
        self.advance_to_next_token()

        if self._curr_token.ttype != lexer.IDENTIFIER:
            return {'success': False,
                    'error': f'Invalid syntax: Unexpected {self._curr_token.ttype}:"{self._curr_token.value}" instead file_name while parsing.\n'
                             f'Correct syntax: LOAD file_name\n'}

        result['filename'] = self._curr_token.value

        self.advance_to_next_token()
        if self._curr_token.ttype != 'EOF':
            return {'success': False,
                    'error': f'Invalid syntax: Unexpected {self._curr_token.ttype}:"{self._curr_token.value}" instead EOF while parsing.\n'
                             f'Correct syntax: LOAD file_name\n'}

        return result

    def parse_save(self) -> dict:
        return self.parse_command('SAVE')

    def parse_exit(self) -> dict:
        return self.parse_command('EXIT')

    def parse_command(self, command_name) -> dict:
        result = {
            'success': True,
            'command': self._curr_token.value
        }
        self.advance_to_next_token()

        if self._curr_token.ttype != 'EOF':
            return {'success': False,
                    'error': f'Invalid syntax: Unexpected {self._curr_token.ttype}:"{self._curr_token.value}" instead EOF while parsing.\n'
                             f'Correct syntax: {command_name}\n'}

        return result

    def parse(self) -> dict:
        command_handlers = {
            'CREATE': self.parse_create,
            'INSERT': self.parse_insert,
            'SELECT': self.parse_select,
            'LOAD': self.parse_load,
            'SAVE': self.parse_save,
            'EXIT': self.parse_exit
        }

        if isinstance(self._curr_token.value, str):
            command = self._curr_token.value.upper()

            if command in command_handlers:
                return command_handlers[command]()

        return {'success': False, 'error': 'Error: Unknown command.\n'}
