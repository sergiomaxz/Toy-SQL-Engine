from FlorianDB import Interpreter, FlorianDB
from lexer import Lexer
from SQLparser import Parser


def main():
    db = FlorianDB()
    while True:
        packed_input = []
        while True:
            try:
                if not packed_input:
                    raw_input = str(input('>>> '))
                else:
                    raw_input = str(input('...    '))
            except EOFError:
                break

            if ';' in raw_input:
                raw_input = raw_input[:raw_input.index(';')]
                packed_input.append(raw_input)
                break

            packed_input.append(raw_input)

        packed_input = ' '.join(packed_input).strip()
        lexer = Lexer(packed_input)
        parser = Parser(lexer)
        Interpreter(db, parser).interpret()


if __name__ == '__main__':
    main()
