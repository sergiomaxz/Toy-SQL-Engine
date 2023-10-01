import re
import os
import FlorianDB
from SQLparser import Parser


def main():
    while True:
        packed_input = []
        while True:
            if not packed_input:
                try:
                    raw_input = str(input('>>> '))
                except EOFError:
                    break
            else:
                raw_input = str(input('...    '))

            if ';' in raw_input:
                raw_input = raw_input[:raw_input.index(';')]
                packed_input.append(raw_input)
                break

            packed_input.append(raw_input)

        packed_input = ' '.join(packed_input)
        parse = Parser().parse(packed_input)
        for el in parse:
            print(el)


if __name__ == '__main__':
    main()
