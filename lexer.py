import re
from additional_functions import consume

PROCESS_AS_KEYWORD = object()

# Define token types
WHITESPACE, KEYWORD, IDENTIFIER, QUOTES, NUMBER, OPERATOR, PUNCTUATION, PARENTHESES = (
    'WHITESPACE', 'KEYWORD', 'IDENTIFIER', 'QUOTES', 'NUMBER', 'OPERATOR', 'PUNCTUATION', 'PARENTHESES'
)

# Define regular expressions for SQL tokens
SQL_REGEX = [
    (r'\s+', WHITESPACE),                                 # sql_whitespace
    (r'(?i)VALUES', KEYWORD),                             # sql_keywords
    (r'[a-zA-Z][a-zA-Z0-9_]*', PROCESS_AS_KEYWORD),       # sql_process_as_keyword
    (r"'(''|\\'|[^'])*'", QUOTES),                        # sql_string_single_quote
    (r'"(""|\\"|[^"])*"', QUOTES),                        # sql_string_double_quotes
    (r'-?[\d][\d.]*', NUMBER),                            # sql_number_literal
    (r'[=<>]', OPERATOR),                                 # sql_operators
    (r'[.,;]', PUNCTUATION),                              # sql_punctuation
    (r'[()]', PARENTHESES)                                # sql_parentheses
]

KEYWORDS = ['CREATE', 'INSERT', 'INTO', 'VALUES', 'SELECT', 'FROM', 'WHERE', 'OR', 'AND']


class Token:
    def __init__(self, value, ttype):
        self.value = value
        self.ttype = ttype


class Lexer:
    def __init__(self, sql):
        self._SQL_REGEX = [
            (re.compile(rx, re.IGNORECASE | re.UNICODE).match, tt)
            for rx, tt in SQL_REGEX
        ]

        self._keywords = KEYWORDS

        self.tokens = self.get_tokens(sql)
        self._current_token = Token(None, None)

    def get_next_token(self) -> Token:
        while self._current_token.ttype != 'EOF':
            self._current_token = next(self.tokens, Token(None, 'EOF'))

            if self._current_token.ttype == WHITESPACE:
                continue

            return self._current_token
        return Token(None, 'EOF')

    # Define re is a keyword or identifier
    def is_keyword(self, value: str) -> tuple:
        val = value.upper()
        if val in self._keywords:
            return value, KEYWORD
        else:
            return value, IDENTIFIER

    # Tokenize SQL input
    def get_tokens(self, sql: str):
        iterator = enumerate(sql)
        for pos, char in iterator:
            for rematch, tt in self._SQL_REGEX:
                match = rematch(sql, pos)

                if not match:
                    continue
                elif tt is PROCESS_AS_KEYWORD:
                    tvalue, ttype = self.is_keyword(match.group())
                    yield Token(tvalue, ttype)
                elif tt is NUMBER:
                    yield Token(int(match.group()), tt)
                elif tt is QUOTES:
                    yield Token(match.group()[1:-1], tt)
                else:
                    yield Token(match.group(), tt)

                consume(iterator, match.end() - pos - 1)
                break
