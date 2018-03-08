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
    tokens = parse_unary_op(tokens, ['NOT'], reverse=True, sub=False)
    tokens = parse_binary_op(tokens, ['AND'], reverse=False, sub=False)
    tokens = parse_binary_op(tokens, ['OR'], reverse=False, sub=False)
    tokens = parse_binary_op(tokens, ['IMPLIES'], reverse=True, sub=False)
    tokens = parse_binary_op(tokens, ['EQUIV'], reverse=False, sub=False)
    tokens = parse_unary_op(tokens, ['EXISTS', 'FORALL'], reverse=True, sub=False)
    tokens = parse_unary_op(tokens, ['PREVIOUS', 'NEXT', 'ONCE', 'ALWAYS'], reverse=True, sub=False)
    tokens = parse_binary_op(tokens, ['SINCE'], reverse=True, sub=False)
    if len(tokens) == 1:
        if isinstance(tokens[0], Node):
            return tokens[0]
    else:
        raise RuntimeError("Parse failure")


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


def parse_unary_op(tokens, op, reverse, sub):
    new_tokens = []
    if reverse:
        tokens = list(reversed(tokens))
    for i, token in enumerate(tokens):
        if not isinstance(token, Node):
            if token[0] in op:
                if reverse:
                    next_token = tokens[i - 1]
                    if sub:
                        next_next_token = tokens[i - 2]
                else:
                    next_token = tokens[i + 1]
                    if sub:
                        next_next_token = tokens[i + 2]
                if sub:
                    node = UnaryNode(token[0], parse([next_next_token]), parse_sub(next_token))
                else:
                    node = UnaryNode(token[0], parse([next_token]))
                node.child.parent = node
                tokens[i] = node
                new_tokens.pop()
                new_tokens.append(node)
            else:
                new_tokens.append(token)
        else:
            new_tokens.append(token)
    if reverse:
        return list(reversed(new_tokens))
    else:
        return new_tokens


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
                    next_token = tokens[i - 1]
                    if sub:
                        next_next_token = tokens[i - 2]
                    prev_token = tokens[i + 1]
                else:
                    next_token = tokens[i + 1]
                    if sub:
                        next_next_token = tokens[i + 2]
                    prev_token = tokens[i - 1]
                if sub:
                    node = BinaryNode(token[0], parse([prev_token]), parse([next_next_token]), parse_sub(next_token))
                else:
                    node = BinaryNode(token[0], parse([prev_token]), parse([next_token]))
                node.left.parent = node
                node.right.parent = node
                skip_node += 1
                new_tokens.pop()
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
        return token[0][1:-1].split(",")
    else:
        raise RuntimeError("Could not parse sub: " + token[0])









