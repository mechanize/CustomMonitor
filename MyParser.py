class Node:
    pass


class BinaryNode(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.right = right
        self.left = left


class UnaryNode(Node):
    def __init__(self, op, child):
        self.op = op
        self.child = child


class Leaf(Node):
    def __init__(self, t, value):
        self.t = t
        self.value = value


def parse(tokens: [str, str]) -> Node:
    if tokens == [Node]:
        [token] = tokens
        return token
    if len(tokens) == 1:
        parse_Leaf(tokens)
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
    if tokens == [Node]:
        [token] = tokens
        return token
    else:
        raise RuntimeError("Parse failure")


def parse_parentheses(tokens: [str, str]) -> []:
    new_tokens = []
    depth = 0
    in_parenthesis = []
    for token in tokens:
        if depth == 0:
            if token != Node and token[0] == '(':
                depth += 1
            elif token != Node and token[0] == ')':
                raise RuntimeError("Unexpected token: \")\"")
            else:
                new_tokens.append(token)
        else:
            if token != Node and token[0] == '(':
                depth += 1
                in_parenthesis.append(token)
            elif token != Node and token[0] == ')':
                depth -= 1
                if depth == 1:
                    new_tokens.append(parse(in_parenthesis))
                    in_parenthesis = []
    if depth != 0:
        raise RuntimeError("Expected token missing: \")\"")
    return new_tokens


def parse_unary_op(tokens, op, reverse):
    new_tokens = []
    if reverse:
        tokens = reversed(tokens)
    for i, token in enumerate(tokens):
        if token != Node and token[0] in op:
            if reverse:
                index = i - 1
            else:
                index = i + 1
            node = UnaryNode(token[0], parse(tokens[index]))
            tokens[i] = node
            new_tokens.pop()
            new_tokens.append(node)
        else:
            new_tokens.append(token)
    if reverse:
        return reversed(new_tokens)
    else:
        return new_tokens


def parse_binary_op(tokens, op, reverse):
    new_tokens = []
    skip_node = False
    node = None
    if reverse:
        tokens = reversed(tokens)
    for i, token in enumerate(tokens):
        if token != Node and token[0] in op:
            if reverse:
                next_token = tokens[i-1]
                prev_token = tokens[i+1]
            else:
                next_token = tokens[i - 1]
                prev_token = tokens[i + 1]
            node = BinaryNode(token[0], parse(prev_token), parse(next_token))
            skip_node = True
            new_tokens.pop()
            new_tokens.append(node)
        elif skip_node:
            tokens[i] = node
        else:
            new_tokens.append(token)
    if reverse:
        return reversed(new_tokens)
    else:
        return new_tokens


def parse_Leaf(tokens):
    return Leaf(tokens[0][1], tokens[0][0])







