import lexer

P_OPEN = '('
P_CLOSE = ')'


class Parser:
    def __init__(self):
        self._tokens = None
        self._current_token = None

    def eat(self):
        self._current_token = next(self._tokens, lexer.Token(None, 'EOF'))

    def factor(self):
        token = self._current_token
        if (token.ttype, token.value) == (lexer.PARENTHESES, P_OPEN):
            result = [token.value]
            self.eat()
            result.extend(self.group_general())
            if (self._current_token.ttype, self._current_token.value) == (lexer.PARENTHESES, P_CLOSE):
                result.append(self._current_token.value)
                self.eat()
            return result
        else:
            self.eat()
            return token

    def term(self) -> list:
        result = []
        tmp_token = self.factor()

        result.append(tmp_token.value) if isinstance(tmp_token, lexer.Token) else result.append(tmp_token)

        if isinstance(tmp_token, list) or tmp_token.ttype in (lexer.IDENTIFIER, lexer.QUOTES, lexer.NUMBER):
            while self._current_token.ttype in (lexer.WHITESPACE, lexer.PUNCTUATION, lexer.OPERATOR):
                if self._current_token.ttype in (lexer.OPERATOR, lexer.PUNCTUATION):
                    result.append(self._current_token.value)
                    self.eat()
                if self._current_token.ttype == lexer.WHITESPACE:
                    self.eat()
                tmp_token = self.factor()
                if isinstance(tmp_token, lexer.Token):
                    result.append(tmp_token.value)
                    if tmp_token.ttype == lexer.KEYWORD:
                        break
                else:
                    result.append(tmp_token)

        return result

    def group_general(self) -> list:
        if self._current_token.ttype == lexer.WHITESPACE:
            self.eat()
        result = []
        result.extend(self.term())

        while self._current_token.ttype == lexer.WHITESPACE:
            self.eat()
            result.extend(self.term())

        return result

    def group_where(self):
        result = []

        if type(self._tokens) is list:
            self._tokens = iter(self._tokens)

        for gtoken in self._tokens:
            result.append(gtoken)
            if type(gtoken) is str and gtoken.upper() == "WHERE":
                tmp_group = []
                for el in self._tokens:
                    tmp_group.append(el)
                result.append(tmp_group)

        return result

    def group(self):
        for func in [self.group_general, self.group_where]:
            self._tokens = func()
        return self._tokens

    def parse(self, sql_statement: str) -> list:
        tokens_stream = lexer.tokenize_sql(sql_statement)
        self._tokens = tokens_stream
        self._current_token = next(self._tokens)
        parsed_query = self.group()
        return parsed_query
