from AST import *
from Op import *
from Context import Context


def evaluate(node: Node, data: dict, context: Context) -> Table:
    context.current = []
    visit(node, data, context)
    return context.current[-1]


def visit(node: Node, data: dict, context: Context) -> EvalObject:
    if isinstance(node, BinaryNode):
        if node.op in ['=', '<', '>', '>=', '<=']:
            if node.visited:
                previous = context.previous[context.get_current_index()]
                res = Table(table_copy(previous.name, context), previous.fv, previous.is_negative)
            else:
                res = visit_condition(node, context)
                node.visited = True
        else:
            left = visit(node.left, data, context)
            right = visit(node.right, data, context)
            if node.op in ['*', '/', 'MOD', '+', '-']:
                raise RuntimeError("Arithmetic operator without condition operator found in" + node.to_str())
            elif node.op == 'OR':
                res = union(left, right, context)
            elif node.op == 'AND':
                res = intersection(left, right, context)
            elif node.op == 'IMPLIES':
                res = union(negation(left, context), right, context)
            elif node.op == 'EQUIV':
                if isinstance(left, Table) and isinstance(right, Table):
                    l_tuples = get_tuples(left.name, left.fv, context)
                    r_tuples = get_tuples(right.name, right.fv, context)
                    if l_tuples == r_tuples:
                        res = Bool(True)
                    else:
                        res = Bool(False)
                else:
                    raise RuntimeError("EQUIV must contain tables on both sides")
            elif node.op == 'SINCE':
                if node.sub:
                    start, end = node.sub
                    ts_diff = context.current_ts - context.previous_ts
                    res = None
                    for to in range(0, end + 1):
                        frm = max(0, to - (end - start))
                        if frm > 0:
                            if ts_diff <= to:
                                res = context.previous[context.get_current_index() - ts_diff]
                            else:
                                res = Bool(False)
                        else:
                            if frm <= ts_diff <= to:
                                previous = context.previous[context.get_current_index() - ts_diff]
                            else:
                                previous = Bool(False)
                            res = union(right, intersection(left, previous, context), context)
                        if to < end:
                            context.current.append(res)

                else:
                    previous = context.previous[context.get_current_index()]
                    res = union(right, intersection(left, previous, context), context)
            else:
                raise RuntimeError("Unhandled operator " + node.op)
    elif isinstance(node, UnaryNode):
        child = visit(node.child, data, context)
        if node.op == 'NOT':
            res = negation(child, context)
        elif node.op == 'EXISTS':
            if isinstance(child, Table):
                if set(node.sub).issubset([e[0] for e in child.fv]):
                    fv = set()
                    for e in child.fv:
                        if not e[0] in node.sub:
                            fv.add(e)
                    if fv == set():
                        if child.is_negative:
                            res = Bool(False)
                        else:
                            if get_tuples(child.name, child.fv, context):
                                res = Bool(True)
                            else:
                                res = Bool(False)
                    else:
                        if child.is_negative:
                            res = Table(empty_table(fv, context), fv, child.is_negative)
                        else:
                            res = Table(projection(child.name, fv, context), fv, child.is_negative)
                else:
                    raise RuntimeError("EXISTS: %s has to be subset of %s" % (node.sub, child.fv))
            else:
                raise RuntimeError("EXISTS of non-Table not supported")
        elif node.op == 'FORALL':
            if isinstance(child, Table):
                if set(node.sub).issubset(child.fv):
                    fv = child.fv.difference(set(node.sub))
                    if fv == set():
                        if child.is_negative:
                            if get_tuples(child.name, child.fv, context):
                                res = Bool(True)
                            else:
                                res = Bool(False)
                        else:
                            res = Bool(False)
                    else:
                        if child.is_negative:
                            res = Table(projection(child.name, fv, context), fv, child.is_negative)
                        else:
                            res = Table(empty_table(fv, context), fv, child.is_negative)
                else:
                    raise RuntimeError("FORALL: %s has to be subset of %s" % node.sub, child.fv)
            else:
                raise RuntimeError("FORALL of non-Table not supported")
        elif node.op == 'PREVIOUS':
            previous = context.previous[context.get_current_index() - 1]
            if node.sub:
                start, end = node.sub
                ts_diff = context.current_ts - context.previous_ts
                if start <= ts_diff <= end:
                    if isinstance(previous, Table):
                        res = Table(table_copy(previous.name, context), previous.fv, previous.is_negative)
                    else:
                        res = previous
                else:
                    res = Table(empty_table(previous.fv, context), previous.fv, False)
            else:
                if isinstance(previous, Table):
                    res = Table(table_copy(previous.name, context), previous.fv, previous.is_negative)
                else:
                    res = previous
        elif node.op == 'ONCE':
            if node.sub:
                start, end = node.sub
                ts_diff = context.current_ts - context.previous_ts
                res = None
                for to in range(0, end + 1):
                    frm = max(0, to - (end - start))
                    if frm > 0:
                        if ts_diff <= to:
                            res = context.previous[context.get_current_index() - ts_diff]
                        else:
                            res = Bool(False)
                    else:
                        if frm <= ts_diff <= to:
                            previous = context.previous[context.get_current_index() - ts_diff]
                        else:
                            previous = Bool(False)
                        res = union(child, previous, context)
                    if to < end:
                        context.current.append(res)
            else:
                previous = context.previous[context.get_current_index()]
                res = union(child, previous, context)
        elif node.op in ['SUM', 'MIN', 'MAX', 'CNT', 'AVG']:
            if len(node.sub) == 2:
                out, aggreg = node.sub
                res = aggregation(child, node.op, out, aggreg, context)
            elif len(node.sub) == 3:
                out, aggreg, group_by = node.sub
                res = aggregation(child, node.op, out, aggreg, context, group_by)
            else:
                raise RuntimeError("Error parsing aggregation")
        else:
            raise RuntimeError("Unhandled operator: " + node.op)
    elif isinstance(node, Leaf):
        res = parse_leaf(node, data, context)
    else:
        raise RuntimeError("Error while parsing node: " + node.to_str())
    context.current.append(res)

    # if isinstance(res, Table):
    #     if isinstance(node, BinaryNode):
    #         print(res.name, res.fv, node.op, end=" ")
    #         print(get_tuples(res.name, res.fv, context))
    #     elif isinstance(node, UnaryNode):
    #         print(res.name, res.fv, node.op, end=" ")
    #         print(get_tuples(res.name, res.fv, context))
    #     elif isinstance(node, Leaf):
    #         print(res.name, res.fv, node.typ, node.value, end=" ")
    #         print(get_tuples(res.name, res.fv, context))
    # elif isinstance(res, Bool):
    #     if isinstance(node, BinaryNode):
    #         print(res.v, node.op)
    #     elif isinstance(node, UnaryNode):
    #         print(res.v, node.op)
    #     elif isinstance(node, Leaf):
    #         print(res.v, node.typ, node.value)

    return res


def visit_condition(node: BinaryNode, context: Context) -> Table:
    left = node.left
    right = node.right
    if isinstance(left, Leaf) and isinstance(right, Leaf):
        if left.typ == 'VAR' and right.typ == 'INT':
            var = left.value
            const = right.value
            reverse = False
        elif right.typ == 'VAR' and left.typ == 'INT':
            var = right.value
            const = left.value
            reverse = True
        else:
            raise RuntimeError("Condition has to be of type VAR op INT with op in ['=', '<', '>', '>=', '<=']")
    else:
        raise RuntimeError("Condition tree too long")
    if node.op == '=':
        res = Table(table_from_tuples({(var, 'INT')}, [(int(const),)], context), {(var, 'INT')}, False)
    elif node.op == '!=':
        res = Table(table_from_tuples({(var, 'INT')}, [(int(const),)], context), {(var, 'INT')}, True)
    elif node.op == '<' and not reverse or node.op == '>' and reverse:
        res = Table(table_from_tuples({(var, 'INT')}, [(e,) for e in range(int(const))], context)
                    , {(var, 'INT')}, False)
    elif node.op == '<=' and not reverse or node.op == '>=' and reverse:
        res = Table(table_from_tuples({(var, 'INT')}, [(e,) for e in range(int(const) + 1)], context)
                    , {(var, 'INT')}, False)
    elif node.op == '>' and not reverse or node.op == '<' and reverse:
        res = Table(table_from_tuples({(var, 'INT')}, [(e,) for e in range(int(const) + 1)], context)
                    , {(var, 'INT')}, True)
    elif node.op == '>=' and not reverse or node.op == '<=' and reverse:
        res = Table(table_from_tuples({(var, 'INT')}, [(e,) for e in range(int(const))], context)
                    , {(var, 'INT')}, True)
    else:
        raise RuntimeError("Operator not recognized:" + node.op)
    return res


def parse_leaf(node: Leaf, data: dict, context: Context) -> EvalObject:
    if node.typ == 'SIGNATURE':
        sig, params = node.value[:-1].split("(")
        sig_types, tuples = data.get(sig)
        params = params.split(",")
        if params == ['']:
            params = []
        if len(sig_types) != len(params):
            #print(sig_types, params)
            raise RuntimeError("Node " + node.to_str() + " does not match signature ")

        if not params:
            if tuples == [[False]]:
                return Bool(False)
            else:
                return Bool(True)
        else:

            for i, param in enumerate(params):
                if sig_types[i] == 'INT':
                    try:
                        const = int(param)
                        for k, e in enumerate(tuples):
                            if e[i] != const:
                                tuples.pop(k)
                        params[i] = context.get_var_name()
                    except ValueError:
                        pass
                elif sig_types[i] == 'VARCHAR':
                    if param[0] == "\"" and param[-1] == "\"":
                        const = param[1:-1]
                        for k, e in enumerate(tuples):
                            if e[i] != const:
                                tuples.pop(k)
                        params[i] = context.get_var_name()
            fv = list(zip(params, sig_types))
            #print("here ", end="")
            #print(fv, tuples)

            return Table(table_from_tuples(fv, tuples, context), set(fv), False)
    else:
        raise RuntimeError("Unhandled type for Leaf outside condition: " + node.typ)
