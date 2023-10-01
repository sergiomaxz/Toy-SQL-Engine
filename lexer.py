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
    (r'[a-zA-Z_][a-zA-Z0-9_]*', PROCESS_AS_KEYWORD),      # sql_process_as_keyword
    (r"'(''|\\'|[^'])*'", QUOTES),                        # sql_string_single_quote
    (r'"(""|\\"|[^"])*"', QUOTES),                        # sql_string_double_quotes
    # r"'[^']*'",                                         # sql_string_literal
    (r'[\d][\d.]*', NUMBER),                              # sql_number_literal
    # r'\w[$#\w]*',                                       # process as keyword
    (r'[=<>]+', OPERATOR),                                # sql_operators
    (r'[.,;]', PUNCTUATION),                              # sql_punctuation
    (r'[()]', PARENTHESES)                                # sql_parentheses
]

KEYWORDS = ['CREATE', 'INSERT', 'INTO', 'VALUES', 'SELECT', 'FROM', 'WHERE', 'OR', 'AND']


class Token:
    def __init__(self, value, ttype):
        self.value = value
        self.ttype = ttype


class Lexer:
    def __init__(self):
        self._SQL_REGEX = [
            (re.compile(rx, re.IGNORECASE | re.UNICODE).match, tt)
            for rx, tt in SQL_REGEX
        ]

        self._keywords = KEYWORDS

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
                else:
                    yield Token(match.group(), tt)

                consume(iterator, match.end() - pos - 1)
                break


def tokenize_sql(sql):
    return Lexer().get_tokens(sql)
