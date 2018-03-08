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
                    name = inner_join(first.name, second.name, first.fv, second.fv, context)
                return Table(name, first.fv.union(second.fv), True)
            elif first.is_negative and not second.is_negative:
                name = diff(first.name, second.name, first.fv, second.fv, context)
                return Table(name, first.fv, True)
            elif not first.is_negative and second.is_negative:
                name = diff(second.name, first.name, second.fv, first.fv, context)
                return Table(name, second.fv, True)
            else:
                join_variables = first.fv.intersection(second.fv)
                if join_variables == {}:
                    name = cross_join(first.name, second.name, context)
                else:
                    name = outer_join(first.name, second.name, first.fv, second.fv, context)
                return Table(name, first.fv.union(second.fv), False)
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
                name = diff(second.name, first.name, second.fv, first.fv, context)
                return Table(name, first.fv, False)
            elif not first.is_negative and second.is_negative:
                name = diff(first.name, second.name, first.fv, second.fv, context)
                return Table(name, second.fv, False)
            else:
                join_variables = first.fv.intersection(second.fv)
                if join_variables == {}:
                    name = empty_table(first.fv.union(second.fv), context)
                else:
                    name = inner_join(first.name, second.name, first.fv, second.fv, context)
                return Table(name, first.fv.union(second.fv), False)
    else:
        raise RuntimeError("intersection:", first, second)


def negation(v: EvalObject, context: Context) -> EvalObject:
    if isinstance(v, Bool):
        return Bool(not v.v)

    elif isinstance(v, Condition):
        return Not(v)

    elif isinstance(v, Table):
        return Table(table_copy(v.name, context), v.fv, not v.is_negative)

    else:
        raise RuntimeError("negation:", v)


def table_with_condition(table: Table, condition: Condition, context: Context) -> Table:
    sql = """CREATE TABLE {dest} AS
             SELECT * FROM {src}
             WHERE {condition} """
    name = context.get_table_name()
    context.cursor.execute(sql.format(dest=name, src=table.name, condition=condition.to_str()))
    context.conn.commit()
    return Table(name, table.fv, table.is_negative)


def inner_join(first: str, second: str, first_fv: {str, str}, second_fv: {str, str}, context: Context) -> str:
    sql = """CREATE TABLE {dest} AS
             SELECT {selection} FROM {src1}
             INNER JOIN {src2}
             ON {join_condition} ;"""
    name = context.get_table_name()
    join_variables = first_fv.intersection(second_fv)
    other_variables = first_fv.union(second_fv).difference(join_variables)
    join_condition = " AND ".join(["".join([first, ".", e, " = ", second, ".", e]) for e, _ in join_variables])
    selection = ", ".join([e for e, _ in other_variables] + [first + "." + e for e, _ in join_variables])
    context.cursor.execute(
        sql.format(dest=name, src1=first, src2=second, selection=selection, join_condition=join_condition))
    context.conn.commit()
    return name


def outer_join(first: str, second: str, first_fv: {str, str}, second_fv: {str, str},  context: Context) -> str:
    join_variables = first_fv.intersection(second_fv)
    first_only = first_fv.difference(second_fv)
    second_only = second_fv.difference(first_fv)
    sql = """CREATE TABLE {dest} AS
             SELECT {varlist1} FROM {src1}
             LEFT JOIN {src2}
             ON {join_condition}
             UNION
             SELECT {varlist2} FROM {src2}
             LEFT JOIN {src1}
             ON {join_condition} """
    name = context.get_table_name()
    varlist1 = ", ".join([first + "." + e for e, _ in first_only] + [first + "." + e for e, _ in join_variables]
                         + [second + "." + e for e, _ in second_only])
    varlist2 = ", ".join([first + "." + e for e, _ in first_only] + [second + "." + e for e, _ in join_variables]
                         + [second + "." + e for e, _ in second_only])
    join_condition = " AND ".join(["".join([first, ".", e, " = ", second, ".", e]) for e, _ in join_variables])
    context.cursor.execute(sql.format(dest=name, src1=first, src2=second, varlist1=varlist1, varlist2=varlist2,
                                      join_condition=join_condition))
    context.conn.commit()
    return name


def cross_join(first: str, second: str, context: Context) -> str:
    sql = """CREATE TABLE {dest} AS
             SELECT * FROM {src1}
             CROSS JOIN {src2} """
    name = context.get_table_name()
    context.cursor.execute(sql.format(dest=name, src1=first, src2=second))
    context.conn.commit()
    return name


def diff(first: str, second: str, first_fv: {str, str}, second_fv: {str, str}, context: Context) -> str:
    if not second_fv.issubset(first_fv):
        raise RuntimeError("For A \\ B, B has to be subset of A")
    join_variables = second_fv
    sql = """CREATE TABLE {dest} AS
             SELECT {varlist0} FROM
            (SELECT {varlist1} FROM {src1}
             EXCEPT
             SELECT {varlist2} FROM {src2}) AS Some_table
             INNER JOIN {src1} ON {join_condition} """
    name = context.get_table_name()
    varlist0 = ", ".join([first + "." + e for e, _ in first_fv])
    varlist1 = ", ".join([first + "." + e for e, _ in join_variables])
    varlist2 = ", ".join([second + "." + e for e, _ in join_variables])
    join_condition = " AND ".join([first + "." + e + " = Some_table." + e for e, _ in join_variables])
    #print("diff: ", end="")
    #print(sql.format(dest=name, varlist0=varlist0, varlist1=varlist1, varlist2=varlist2, src1=first,
    #                 src2=second, join_condition=join_condition))
    context.cursor.execute(sql.format(dest=name, varlist0=varlist0, varlist1=varlist1, varlist2=varlist2, src1=first,
                                      src2=second, join_condition=join_condition))
    context.conn.commit()
    return name


def empty_table(fv: {str, str}, context: Context) -> str:
    sql = """CREATE TABLE {dest} (
             {varlist} );"""
    name = context.get_table_name()
    var_list = ",\n".join([e + " " + i for e, i in fv])
    context.cursor.execute(sql.format(dest=name, varlist=var_list))
    context.conn.commit()
    return name


def table_copy(first: str, context: Context) -> str:

    sql = """CREATE TABLE {dest} AS
            SELECT * FROM {src}; """
    name = context.get_table_name()
    context.cursor.execute(sql.format(dest=name, src=first))
    context.conn.commit()

    return name


def projection(first: str, fv: {str, str}, context: Context) -> str:
    sql = """CREATE TABLE {dest} AS 
             SELECT {varlist} FROM {src} """
    name = context.get_table_name()
    varlist = ", ".join([first + "." + e for e, _ in fv])
    context.cursor.execute(sql.format(dest=name, varlist=varlist, src=first))
    context.conn.commit()
    return name


def get_tuples(table: str, fv: {(str, str)}, context: Context) -> [tuple]:
    sql = """SELECT {varlist} FROM {src} """
    varlist = ", ".join([e for e, _ in fv])
    tuples = []
    for t in context.cursor.execute(sql.format(src=table, varlist=varlist)):
        tuples.append(t)
    context.conn.commit()
    return tuples


def table_from_tuples(fv: [(str, str)] or [[str, str]], tuples: [tuple], context: Context) -> str:
    sql = """CREATE TABLE {name} (
             {varlist} );"""
    name = context.get_table_name()
    var_list = ",\n".join([e + " " + i for e, i in fv])
    varlist2 = ", ".join([e for e, _ in fv])
    sql2 = """INSERT INTO {dest} ({varlist2}) VALUES ({values});"""
    with context.conn:
        #print(sql.format(name=name, varlist=var_list))
        context.cursor.execute(sql.format(name=name, varlist=var_list))
        for t in tuples:
            #print(sql2.format(dest=name, varlist2=varlist2, values=", ".join([format_value(e) for e in t])))
            context.cursor.execute(sql2.format(dest=name, varlist2=varlist2, values=", ".join([format_value(e) for e in t])))
    return name


def format_value(value: int or str) -> str:
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return "\"" + value + "\""
