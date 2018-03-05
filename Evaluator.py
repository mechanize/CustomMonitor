from AST import *
from Op import *
from Context import Context


def evaluate(node: Node, data: dict, context: Context) -> EvalObject:
    context.previous = context.current
    context.current = []
    visit(node, data, context)
    return context.current[-1]


def visit(node: Node, data: dict, context: Context) -> EvalObject:
    if isinstance(node, BinaryNode):
        left = visit(node.left, data, context)
        right = visit(node.right, data, context)
        if node.op in ['*', '/', 'MOD', '+', '-', '=', '<', '>', '>=', '<=']:
            if node.visited:
                res = context.previous[context.get_current_index()]
            else:
                res = visit_condition(node, context)
                node.visited = True
        elif node.op == 'OR':
            res = union(left, right, context)
        elif node.op == 'AND':
            res = intersection(left, right, context)
        elif node.op == 'IMPLIES':
            res = union(negation(left, context), right, context)
        elif node.op == 'EQUIV':
            if isinstance(left, Table) and isinstance(right, Table):
                l_tuples = get_tuples(left.name, context)
                r_tuples = get_tuples(right.name, context)
                if l_tuples == r_tuples:
                    res = Bool(True)
                else:
                    res = Bool(False)
            else:
                raise RuntimeError("EQUIV must contain tables on both sides")
        elif node.op == 'SINCE':
            previous = context.previous[context.get_current_index()]
            res = union(right, intersection(left, previous, context), context)
        else:
            raise RuntimeError("Unhandled operator " + node.op)
    elif isinstance(node, UnaryNode):
        child = visit(node, data, context)
        if node.op == 'NOT':
            res = negation(node.child, context)
        elif node.op == 'EXISTS' or node.op == 'FORALL':  # TODO: Check if FORALL works the same way as EXISTS
            if isinstance(child, Table):
                if set(node.sub).issubset(child.fv):
                    fv = child.fv.difference(set(node.sub))
                    res = Table(projection(child.name, fv, context), fv, child.is_negative)
                else:
                    raise RuntimeError("EXISTS, FORALL: %s has to be subset of %s" % node.sub, child.fv)
            else:
                raise RuntimeError("EXISTS, FORALL of non-Table not supported")
        elif node.op == 'PREVIOUS':
            res = context.previous[context.get_current_index()]
        elif node.op == 'ONCE':
            previous = context.previous[context.get_current_index()]
            res = union(child, previous, context)
        else:
            raise RuntimeError("Unhandled operator: " + node.op)
    elif isinstance(node, Leaf):  # TODO
        if node.typ == 'SIGNATURE':
            sig, params = node.value[:-1].split("(")
            tuples = data.get(sig)
            for param in params.split(","):
                res = None
        res = None
    else:
        raise RuntimeError("Error while parsing node: " + node.to_str())
    context.current.append(res)
    return res








def visit_condition(node: Node, context: Context) -> Condition:
    return Condition()  # TODO
