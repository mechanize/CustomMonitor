from AST import *


def parse(tokens: [str, str]) -> Node:

    if len(tokens) == 1:
        if isinstance(tokens[0], Node):
            return tokens[0]
        return parse_leaf(tokens)
    tokens = parse_parentheses(tokens)
    tokens = parse_binary_op(tokens, ['*', '/', 'MOD'], reverse=False)
    tokens = parse_binary_op(tokens, ['+', '-'], reverse=False)
    tokens = parse_binary_op(tokens, ['=', '<', '>', '<=', '>='], reverse=False)
    tokens = parse_unary_op(tokens, ['NOT'], reverse=True)
    tokens = parse_binary_op(tokens, ['AND'], reverse=False)
    tokens = parse_binary_op(tokens, ['OR'], reverse=False)
    tokens = parse_binary_op(tokens, ['IMPLIES'], reverse=True)
    tokens = parse_binary_op(tokens, ['EQUIV'], reverse=False)
    tokens = parse_unary_op(tokens, ['EXISTS', 'FORALL'], reverse=True)
    tokens = parse_unary_op(tokens, ['PREVIOUS', 'NEXT', 'ONCE', 'ALWAYS'], reverse=True)
    tokens = parse_binary_op(tokens, ['SINCE'], reverse=True)
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


def parse_unary_op(tokens, op, reverse):
    new_tokens = []
    if reverse:
        tokens = list(reversed(tokens))
    for i, token in enumerate(tokens):
        if not isinstance(token, Node):
            if token[0] in op:
                if reverse:
                    index = i - 1
                else:
                    index = i + 1
                node = UnaryNode(token[0], parse([tokens[index]]))
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


def parse_binary_op(tokens, op, reverse):
    new_tokens = []
    skip_node = False
    node = None
    if reverse:
        tokens = list(reversed(tokens))
    for i, token in enumerate(tokens):
        if skip_node:
            skip_node = False
            continue
        if not isinstance(token, Node):
            if token[0] in op:
                if reverse:
                    next_token = tokens[i-1]
                    prev_token = tokens[i+1]
                else:
                    next_token = tokens[i+1]
                    prev_token = tokens[i-1]
                node = BinaryNode(token[0], parse([prev_token]), parse([next_token]))
                node.left.parent = node
                node.right.parent = node
                skip_node = True
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








