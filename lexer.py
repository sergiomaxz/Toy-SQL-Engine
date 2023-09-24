import re
from additional_functions import consume

# Define regular expressions for SQL tokens
SQL_REGEX = [
    r'\s+',                         # sql_whitespace
    r'(?i)VALUES',                  # sql_keywords
    r'[a-zA-Z_][a-zA-Z0-9_]*',      # sql_identifier
    r"'(''|\\'|[^'])*'",            # sql_string_single_quote
    r'"(""|\\"|[^"])*"',            # sql_string_double_quotes
    r"'[^']*'",                     # sql_string_literal
    r'\d+',                         # sql_number_literal
    r'\w[$#\w]*',                   # process as keyword
    r'[=<>]+',                      # sql_operators
    r'[.,;()]'                      # sql_punctuation
]


class Lexer:
    def __init__(self):
        self._SQL_REGEX = [
            re.compile(rx, re.IGNORECASE | re.UNICODE).match
            for rx in SQL_REGEX
        ]

        self._keywords = ['CREATE', 'INSERT', 'INTO', 'VALUES', 'SELECT', 'FROM', 'WHERE', 'OR', 'AND']

    # Tokenize SQL input
    def get_tokens(self, sql):
        tokens = []
        iterator = enumerate(sql)
        for pos, char in iterator:
            for rematch in self._SQL_REGEX:
                match = rematch(sql, pos)

                if not match:
                    continue
                else:
                    tokens.append(match.group())

                consume(iterator, match.end() - pos - 1)
                break

        # another variant

        # for match in re.finditer(sql_pattern, sql):
        #     if match.group() is not None:
        #         tokens.append((match.group(), match.start(), match.end()))

        return tokens


def tokenize_sql(sql):
    return Lexer().get_tokens(sql)
