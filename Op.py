import Context


class EvalObject:
    pass


class Table(EvalObject):
    def __init__(self, name, fv, is_negative):
        self.is_negative = is_negative
        self.name = name
        self.fv = fv


class Bool(EvalObject):
    def __init__(self, v):
        self.v = v


class Condition(EvalObject):
    def to_str(self):
        pass


class And(Condition):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_str(self):
        return "(" + self.left.to_str() + ") AND (" + self.left.to_str + ")"


class Or(Condition):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_str(self):
        return "(" + self.left.to_str() + ") OR (" + self.left.to_str + ")"


class Not(Condition):
    def __init__(self, v):
        self.v = v

    def to_str(self):
        return "NOT (" + self.v.to_str() + ")"


class Id(Condition):
    def __init__(self, v):
        self.v = v

    def to_str(self):
        return self.v


def union(first: EvalObject, second: EvalObject, context: Context) -> EvalObject:
    if isinstance(first, Bool):
        if isinstance(second, Table):
            if first.v:
                return Table(empty_table(second.fv, context), second.fv, True)
            else:
                return Table(table_copy(second.name, context), second.fv, second.is_negative)
        elif isinstance(second, Condition):
            if first.v:
                return Bool(True)
            else:
                return second
        elif isinstance(second, Bool):
            return Bool(first.v or second.v)

    elif isinstance(first, Condition):
        if isinstance(second, Bool):
            if second.v:
                return Bool(True)
            else:
                return first
        elif isinstance(second, Condition):
            return Or(first, second)
        elif isinstance(second, Table):
            return table_with_condition(table=second, condition=first, context=context)

    elif isinstance(first, Table):
        if isinstance(second, Bool):
            if second.v:
                return Table(empty_table(first.fv, context), first.fv, True)
            else:
                return Table(table_copy(first.name, context), first.fv, first.is_negative)
        elif isinstance(second, Condition):
            return table_with_condition(table=first, condition=second, context=context)
        elif isinstance(second, Table):
            if first.is_negative and second.is_negative:
                join_variables = first.fv.intersection(second.fv)
                if join_variables == {}:
                    name = empty_table(first.fv.union(second.fv), context)
                else:
                    name = inner_join(first.name, second.name, first.fv.intersection(second.fv), context)
                return Table(name, first.fv.union(second.fv), True)
            elif first.is_negative and not second.is_negative:
                name = diff(first.name, second.name, first.fv.union(second.fv), context)
                return Table(name, first.fv, True)
            elif not first.is_negative and second.is_negative:
                name = diff(second.name, first.name, first.fv.union(second.fv), context)
                return Table(name, second.fv, True)
            else:
                join_variables = first.fv.intersection(second.fv)
                if join_variables == {}:
                    name = cross_join(first.name, second.name, context)
                else:
                    name = outer_join(first.name, second.name, first.fv.intersection(second.fv), context)
                return Table(name, first.fv.union(second.fv), True)
    else:
        raise RuntimeError("union:", first, second)


def intersection(first: EvalObject, second: EvalObject, context: Context) -> EvalObject:
    if isinstance(first, Bool):
        if isinstance(second, Table):
            if first.v:
                return Table(table_copy(second.name, context), second.fv, second.is_negative)
            else:
                return Table(empty_table(second.fv, context), second.fv, False)
        elif isinstance(second, Condition):
            if first.v:
                return second
            else:
                return Bool(False)
        elif isinstance(second, Bool):
            return Bool(first.v and second.v)  # Works for Conditions and bool for any value of first

    elif isinstance(first, Condition):
        if isinstance(second, Bool):
            if second.v:
                return first
            else:
                return Bool(False)
        elif isinstance(second, Condition):
            return And(first, second)
        elif isinstance(second, Table):
            return table_with_condition(table=second, condition=first, context=context)

    elif isinstance(first, Table):
        if isinstance(second, bool):
            if second:
                return Table(table_copy(first.name, context), first.fv, first.is_negative)
            else:
                return Table(empty_table(first.fv, context), first.fv, False)
        elif isinstance(second, Condition):
            return table_with_condition(table=first, condition=second, context=context)
        elif isinstance(second, Table):
            if first.is_negative and second.is_negative:
                join_variables = first.fv.intersection(second.fv)
                if join_variables == {}:
                    name = cross_join(first.name, second.name, context)
                else:
                    name = outer_join(first.name, second.name, first.fv.intersection(second.fv), context)
                return Table(name, first.fv.union(second.fv), True)
            elif first.is_negative and not second.is_negative:
                name = diff(second.name, first.name, first.fv.union(second.fv), context)
                return Table(name, first.fv, False)
            elif not first.is_negative and second.is_negative:
                name = diff(first.name, second.name, first.fv.union(second.fv), context)
                return Table(name, second.fv, False)
            else:
                join_variables = first.fv.intersection(second.fv)
                if join_variables == {}:
                    name = empty_table(first.fv.union(second.fv), context)
                else:
                    name = inner_join(first.name, second.name, first.fv.intersection(second.fv), context)
                return Table(name, first.fv.union(second.fv), True)
    else:
        raise RuntimeError("intersection:", first, second)


def negation(v: EvalObject, context: Context) -> EvalObject:
    if isinstance(v, Bool):
        return Bool(not v.v)

    elif isinstance(v, Condition):
        return Not(v)

    elif isinstance(v, Table):
        return Table(empty_table(v.fv, context), v.fv, not v.is_negative)

    else:
        raise RuntimeError("negation:", v)


def table_with_condition(table: Table, condition: Condition, context: Context) -> Table:
    sql = """INSERT INTO ?
             SELECT * FROM ? 
             WHERE ? """
    name = context.get_table_name()
    context.cursor.execute(sql, name, table.name, condition.to_str())
    context.cursor.commit()
    return Table(name, table.fv, table.is_negative)


def inner_join(first: str, second: str, join_variables: {str}, context: Context) -> str:
    sql = """INSERT INTO ? 
             SELECT * FROM ?
             INNER JOIN ?
             ON ? """
    name = context.get_table_name()
    join_condition = " AND ".join(["".join([first, ".", e, " = ", second, ".", e]) for e, _ in join_variables])
    context.cursor.execute(sql, name, first, second, join_condition)
    context.cursor.commit()
    return name


def outer_join(first: str, second: str, join_variables: {str},  context: Context) -> str:
    sql = """INSERT INTO ? 
             SELECT * FROM ?
             LEFT JOIN ?
             ON ?
             UNION ALL 
             SELECT * FROM ?
             LEFT JOIN ?
             ON ? """
    name = context.get_table_name()
    join_condition = " AND ".join(["".join([first, ".", e, " = ", second, ".", e]) for e, _ in join_variables])
    context.cursor.execute(sql, name, first, second, join_condition, second, first, join_condition)
    context.cursor.commit()
    return name


def cross_join(first: str, second: str, context: Context) -> str:
    sql = """INSERT INTO ?
             SELECT * FROM ?
             CROSS JOIN ? """
    name = context.get_table_name()
    context.cursor.execute(sql, name, first, second)
    context.cursor.commit()
    return name


def diff(first: str, second: str, join_variables: {str}, context: Context) -> str:
    sql = """INSERT INTO ? 
             SELECT * FROM
            (SELECT ? FROM ?
             EXCEPT
             SELECT ? FROM ?)
             INNER JOIN ? """
    name = context.get_table_name()
    var_list = ", ".join([e for e, _ in join_variables])
    context.cursor.execute(sql, name, var_list, first, var_list, second, first)
    context.cursor.commit()
    return name


def empty_table(fv: {str}, context: Context) -> str:
    sql = """CREATE TABLE ? (
             ? );"""
    name = context.get_table_name()
    var_list = [e + " " + i + ",\n" for e, i in fv]
    context.cursor.execute(sql, name, var_list)
    context.cursor.commit()
    return name


def table_copy(first: str, context: Context) -> str:
    sql = """INSERT INTO ?
             SELECT * FROM ?; """
    name = context.get_table_name()
    context.cursor.execute(sql, name, first)
    context.cursor.commit()
    return name


def projection(first: str, fv: {str}, context: Context) -> str:
    sql = """INSERT INTO ?
             SELECT ? FROM ? """
    name = context.get_table_name()
    varlist = ", ".join([first + "." + e for e in fv])
    context.cursor.execute(sql, name, varlist, first)
    context.cursor.commit()
    return name


def get_tuples(table: str, context: Context) -> [tuple]:
    sql = """SELECT * FROM ? """
    tuples = context.cursor.execute(sql, table)
    context.cursor.commit()
    return tuples
