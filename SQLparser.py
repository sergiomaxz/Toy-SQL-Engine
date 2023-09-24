import lexer
import copy
from additional_functions import consume
# Define regular expressions and lexer (as shown in your previous question)


def consume_whitespaces(tlist):
    result = []
    for pos, token in tlist:
        if token.strip() == '':
            continue
        result.append(token)
    return result


def group_create(tlist):
    result = []
    tmp_list = []
    for pos, token in tlist:
        result.append(token)
        if token.upper() == 'CREATE':
            for pos, token in tlist:
                if token.upper() == 'INDEXED':
                    tmp_list.append(' ')

                elif tmp_list and tmp_list[-1] not in ',()' and token not in ',)' \
                        and token.upper() != 'INDEXED':
                    result.append(''.join(tmp_list))
                    tmp_list = []

                elif token == ')':
                    tmp_list.append(token)
                    result.append(''.join(tmp_list))
                    break

                tmp_list.append(token)
    return result


def group_insert(tlist):
    pass


def group_select(tlist):
    result = []
    for pos, token in tlist:
        result.append(token)
        if token.upper() == 'SELECT':
            united_list = []
            for pos, token in tlist:
                if token.upper() == 'FROM':
                    result.append(','.join(united_list))
                    result.append(token)
                    break

                if token.strip() == '' or token == ',':
                    continue
                else:
                    united_list.append(token)
    return result


def group_where(tlist):
    result = []
    for pos, token in tlist:
        result.append(token)
        if token.upper() == 'WHERE':
            united_list = []
            for pos, token in tlist:
                if token.upper() in ['=', '<', 'OR', 'AND']:
                    united_list.extend([' ', token, ' '])
                else:
                    united_list.append(token)
            result.append(united_list)
    return result


# grouping all categories
def grouping(tokens):
    grouped_tokens = []
    for func in [consume_whitespaces, group_create, group_select, group_where]:
        iterable = enumerate(tokens)
        tokens = func(iterable)

    for pos, token in iterable:
        if token.strip() == '':
            continue

        grouped_tokens.append(token)
        if token.upper() == 'WHERE':
            united_list = []
            for pos, token in iterable:
                if token.strip() == '':
                    continue

                united_list.append(token)
            grouped_tokens.append(united_list)

    # select_clause = parse_select_clause(tokens)
    # from_clause = parse_from_clause(tokens)
    # where_clause = parse_where_clause(tokens)
    return tokens


def parse_select_clause(tokens):
    if tokens[0][0].upper() == 'SELECT':
        tokens.pop(0)  # Consume the 'SELECT' token
        select_items = []
        while tokens[0][0].upper() != 'FROM':
            select_items.append(tokens.pop(0)[0])
        return select_items
    else:
        return []


def parse_from_clause(tokens):
    if tokens[0][0].upper == 'FROM':
        tokens.pop(0)  # Consume the 'FROM' token
        return tokens.pop(0)[0]  # Assume a single table name for simplicity
    else:
        return None


def parse_where_clause(tokens):
    if tokens[0][0].upper() == 'WHERE':
        tokens.pop(0)  # Consume the 'WHERE' token
        conditions = []
        while tokens[0][0] != 'ORDER BY' if 'ORDER BY' in [t[0] for t in tokens] else True:
            conditions.append(tokens.pop(0)[0])
        return conditions
    else:
        return []

def parse(sql_statement):
    tokens = lexer.tokenize_sql(sql_statement)
    parsed_query = grouping(tokens)
    return parsed_query
