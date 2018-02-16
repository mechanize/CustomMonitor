import re

RESERVED = 'RESERVED'
REWRITABLE = 'REWRITABLE'
TEMPORAL = 'TEMPORAL'
INT = 'INT'
VAR = 'VAR'

basic_rules = [
    (r"\(", RESERVED),
    (r"\)", RESERVED),
    (r"IMPLIES", REWRITABLE),
    (r"SINCE", TEMPORAL),
    (r"UNTIL", TEMPORAL),
    (r"NEXT", TEMPORAL),
    (r"PREVIOUS", TEMPORAL),
    (r"ONCE", TEMPORAL),
    (r"EVENTUALLY", TEMPORAL),
    (r"AND", RESERVED),
    (r"OR", RESERVED),
    (r"NOT", RESERVED),
    (r"=", RESERVED),
    (r"<", RESERVED),
    (r">", RESERVED),
    (r"<=", RESERVED),
    (r">=", RESERVED),
    (r"EXISTS", RESERVED),
    (r"FORALL", RESERVED),
    (r"TRUE", RESERVED),
    (r"FALSE", RESERVED),
    (r"[0-9]+", INT),
    (r"[A-Za-z][A-Za-z0-9_]*", VAR)
]


def lex(characters, lexer_rules):
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
            raise RuntimeError("Illegal character \"%s\" at position %d", characters[pos], pos)
        else:
            pos = match.end(0)
    return tokens


def get_rules():
    return basic_rules


