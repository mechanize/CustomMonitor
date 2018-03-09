import re

RESERVED = 'RESERVED'
TEMPORAL = 'TEMPORAL'
INT = 'INT'
VAR = 'VAR'
VARLIST = 'VARLIST'
INTERVAL = 'INTERVAL'
AGGREGATION = 'AGGREGATION'
GROUPBY = 'GROUPBY'

basic_rules = [
    (r'[ \n\t]+', None),
    (r'#[^\n]*', None),
    (r"\(", RESERVED),
    (r"\)", RESERVED),
    (r"IMPLIES", RESERVED),
    (r"\[[0-9]+,[0-9]+\]", INTERVAL),
    (r"SINCE", TEMPORAL),
    (r"PREVIOUS", TEMPORAL),
    (r"ONCE", TEMPORAL),
    (r"AND", RESERVED),
    (r"OR", RESERVED),
    (r"NOT", RESERVED),
    (r"<-", RESERVED),
    (r"SUM", AGGREGATION),
    (r"CNT", AGGREGATION),
    (r"MIN", AGGREGATION),
    (r"MAX", AGGREGATION),
    (r"AVG", AGGREGATION),
    (r";", GROUPBY),
    (r"<=", RESERVED),
    (r">=", RESERVED),
    (r"<", RESERVED),
    (r">", RESERVED),
    (r"=", RESERVED),
    (r"EXISTS", RESERVED),
    (r"FORALL", RESERVED),
    (r"TRUE", RESERVED),
    (r"FALSE", RESERVED),
    ("\.[a-z]+(,[a-z]+)*", VARLIST),
    (r"[0-9]+", INT),
    (r"[A-Za-z][A-Za-z0-9_]*", VAR)
]


def lex(characters, lexer_rules) -> [(str, str)]:
    pos = 0
    tokens = []
    while pos < len(characters):
        match = None
        for rule in lexer_rules:
            pattern, tag = rule
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        if not match:
            raise RuntimeError("Illegal character \"" + characters[pos] + "\" at position " + str(pos))
        else:
            pos = match.end(0)
    print(tokens)
    return tokens


def get_rules():
    return basic_rules


