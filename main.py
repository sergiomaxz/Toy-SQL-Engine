import re
import os
import sqlparse
# import FlorianDB
import SQLparser


def improvedInput():
    packed_input = []
    while True:
        if packed_input == []:
            raw_input = str(input('>>> '))
        else:
            raw_input = str(input('...    '))
        # raw_input = re.sub(" +", " ", raw_input)

        if ';' in raw_input:
            raw_input = raw_input[:raw_input.index(';')]
            packed_input.append(raw_input)
            break

        packed_input.append(raw_input)

    print(packed_input)
    packed_input = ' '.join(packed_input)
    # parse = sqlparse.parse(packed_input)[0]
    parse = SQLparser.parse(packed_input)
    print(parse)
    for p in parse:
        print(p)


if __name__ == '__main__':
    improvedInput()
