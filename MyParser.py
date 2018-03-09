from AST import *


def parse(tokens: [str, str]) -> Node:

    if len(tokens) == 1:
        if isinstance(tokens[0], Node):
            return tokens[0]
        return parse_leaf(tokens)
    tokens = parse_parentheses(tokens)
    tokens = parse_binary_op(tokens, ['*', '/', 'MOD'], reverse=False, sub=False)
    tokens = parse_binary_op(tokens, ['+', '-'], reverse=False, sub=False)
    tokens = parse_binary_op(tokens, ['=', '<', '>', '<=', '>='], reverse=False, sub=False)
    tokens = parse_unary_op(tokens, ['NOT'], sub=False)
    tokens = parse_binary_op(tokens, ['AND'], reverse=False, sub=False)
    tokens = parse_binary_op(tokens, ['OR'], reverse=False, sub=False)
    tokens = parse_binary_op(tokens, ['IMPLIES'], reverse=True, sub=False)
    tokens = parse_binary_op(tokens, ['EQUIV'], reverse=False, sub=False)
    tokens = parse_unary_op(tokens, ['EXISTS', 'FORALL'], sub=True)
    tokens = parse_unary_op(tokens, ['PREVIOUS', 'ONCE'], sub=True)
    tokens = parse_unary_op(tokens, ['ALWAYS'], sub=False)
    tokens = parse_binary_op(tokens, ['SINCE'], reverse=True, sub=True)
    tokens = parse_aggregation(tokens)
    if len(tokens) == 1:
        if isinstance(tokens[0], Node):
            return tokens[0]
    else:
        raise RuntimeError("Parse failure:", tokens)


def parse_parentheses(tokens: [str, str]) -> []:
    new_tokens = []
    depth = 0
    in_parenthesis = []
    for token in tokens:
        if depth == 0:
            if not isinstance(token, Node):
                if token[0] == '(':
                    depth += 1
                elif token[0] == ')':
                    raise RuntimeError("Unexpected token: \")\"")
                else:
                    new_tokens.append(token)
            else:
                new_tokens.append(token)
        else:
            if isinstance(token, Node):
                in_parenthesis.append(token)
            else:
                if token[0] == '(':
                    depth += 1
                    in_parenthesis.append(token)
                elif token[0] == ')':
                    depth -= 1
                    if depth == 0:
                        new_tokens.append(parse(in_parenthesis))
                        in_parenthesis = []
                    else:
                        in_parenthesis.append(token)
                else:
                    in_parenthesis.append(token)

    if depth != 0:
        raise RuntimeError("Expected token missing: \")\"")
    return new_tokens


def parse_unary_op(tokens, op, sub):
    new_tokens = []
    tokens = list(reversed(tokens))
    for i, token in enumerate(tokens):
        if not isinstance(token, Node):
            if token[0] in op:
                next_token = new_tokens.pop()
                if sub and not isinstance(next_token, Node):
                    if next_token[1] in ['INTERVAL', 'VARLIST']:
                        next_next_token = new_tokens.pop()
                        node = UnaryNode(token[0], parse([next_next_token]), parse_sub(next_token))
                    else:
                        node = UnaryNode(token[0], parse([next_token]))
                else:
                    node = UnaryNode(token[0], parse([next_token]))
                new_tokens.append(node)
            else:
                new_tokens.append(token)
        else:
            new_tokens.append(token)
    return list(reversed(new_tokens))


def parse_binary_op(tokens, op, reverse, sub):
    new_tokens = []
    skip_node = 0
    if reverse:
        tokens = list(reversed(tokens))
    for i, token in enumerate(tokens):
        if skip_node:
            skip_node -= 1
            continue
        if not isinstance(token, Node):
            if token[0] in op:
                if reverse:
                    next_token = new_tokens.pop()
                    prev_token = tokens[i + 1]
                else:
                    next_token = tokens[i + 1]
                    prev_token = new_tokens.pop()
                if sub and not isinstance(next_token, Node):
                    if next_token[1] in ['INTERVAL']:
                        if reverse:
                            next_next_token = new_tokens.pop()
                        else:
                            next_next_token = tokens[i + 2]
                            skip_node += 1
                        node = BinaryNode(token[0], parse([prev_token]), parse([next_next_token]), parse_sub(next_token))
                    else:
                        node = BinaryNode(token[0], parse([prev_token]), parse([next_token]))
                        skip_node += 1
                else:
                    node = BinaryNode(token[0], parse([prev_token]), parse([next_token]))
                    skip_node += 1
                new_tokens.append(node)
            else:
                new_tokens.append(token)
        else:
            new_tokens.append(token)
    if reverse:
        return list(reversed(new_tokens))
    else:
        return new_tokens


def parse_leaf(tokens):
    return Leaf(tokens[0][1], tokens[0][0])


def parse_sub(token):
    if token[1] == 'VARLIST':
        return token[0][1:].split(",")
    elif token[1] == 'INTERVAL':
        return [int(e) for e in token[0][1:-1].split(",")]
    else:
        raise RuntimeError("Could not parse sub: " + token[0])


def parse_aggregation(tokens):
    new_tokens = []
    skip_node = 0
    for i, token in enumerate(tokens):
        if skip_node:
            skip_node -= 1
            continue
        if not isinstance(token, Node):
            if token[0] == '<-':
                out = new_tokens.pop()
                op = tokens[i + 1]
                aggreg = tokens[i + 2]
                secondary = [out[0], aggreg[0]]
                if len(tokens) > i + 3:
                    if not isinstance(tokens[i + 3], Node):
                        if tokens[i + 3][0] == ';':
                            secondary.append(parse_sub(tokens[i + 4]))
                            skip_node = 5
                            node = UnaryNode(op[0], parse([tokens[i + 5]]), secondary)
                        else:
                            skip_node = 3
                            node = UnaryNode(op[0], parse([tokens[i + 3]]), secondary)
                    else:
                        skip_node = 3
                        node = UnaryNode(op[0], parse([tokens[i + 3]]), secondary)
                else:
                    skip_node = 3
                    node = UnaryNode(op[0], parse([tokens[i + 3]]), secondary)
                new_tokens.append(node)
            else:
                new_tokens.append(token)
        else:
            new_tokens.append(token)
    return new_tokens










