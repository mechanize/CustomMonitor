

class Table:
    def __init__(self, name, fv, is_negative):
        self.is_negative = is_negative
        self.name = name
        self.fv = fv


class Condition:
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


def union(first, second, context):
    if first is bool:
        if second is Table:
            if first:
                return Table(empty_table(second.fv, context), second.fv, True)
            else:
                return Table(table_copy(second.name, context), second.fv, second.is_negative)
        else:
            return first or second  # Works for Conditions and bool for any value of first

    elif first is Condition:
        if second is bool:
            return second or first
        elif second is Condition:
            return Or(first, second)
        elif second is Table:
            return table_with_condition(table=second, condition=first, context=context)

    elif first is Table:
        if second is bool:
            if second:
                return Table(empty_table(first.fv, context), first.fv, True)
            else:
                return Table(table_copy(first.name, context), first.fv, first.is_negative)
        elif second is Condition:
            return table_with_condition(table=first, condition=second, context=context)
        elif second is Table:
            if first.is_negative and second.is_negative:
                join_variables = first.fv.intersection(second.fv)
                if join_variables == {}:
                    name = empty_table(first.tv.union(second.fv), context)
                else:
                    name = inner_join(first.name, second.name, first.fv.intersection(second.fv), context)
                return Table(name, first.fv.union(second.fv), True)
            elif first.is_negative and not second.is_negative:
                name = diff(first.name, second.name, first.fv.union(second.fv), context)
                return Table(name, first.fv, True)
            elif not first.isnegative and second.is_negative:
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


def intersection(first, second, context):
    if first is bool:
        if second is Table:
            if first:
                return Table(table_copy(second.name, context), first.fv, first.is_negative)
            else:
                return Table(empty_table(second.fv, context), second.fv, False)
        else:
            return first and second  # Works for Conditions and bool for any value of first

    elif first is Condition:
        if second is bool:
            return second and first
        elif second is Condition:
            return And(first, second)
        elif second is Table:
            return table_with_condition(table=second, condition=first, context=context)

    elif first is Table:
        if second is bool:
            if second:
                return Table(table_copy(first.name, context), first.fv, first.is_negative)
            else:
                return Table(empty_table(first.fv, context), first.fv, False)
        elif second is Condition:
            return table_with_condition(table=first, condition=second, context=context)
        elif second is Table:
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
            elif not first.isnegative and second.is_negative:
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


def negation(v, context):
    if v is bool:
        return not v

    elif v is Condition:
        return Not(v)

    elif v is Table:
        return Table(empty_table(v.fv, context), v.fv, not v.is_negative)

    else:
        raise RuntimeError("negation:", v)


def table_with_condition(table, condition, context):
    sql = """SELECT * FROM "{src}" 
             INTO "{destination}" 
             WHERE "{condition}" """
    name = context.get_table_name()
    sql.format(src=table.name, destination=name, condition=condition.to_str())
    context.cursor.execute(sql)
    context.cursor.commit()
    return Table(name, table.fv, table.is_negative)


def inner_join(first, second, join_variables, context):
    sql = """SELECT * FROM "{src1}"
             INNER JOIN "{src2}"
             ON "{join_condition}"
             INTO "{destination}" """
    name = context.get_table_name()
    join_condition = " AND ".join(["".join([first, ".", e, " = ", second, ".", e]) for e, _ in join_variables])
    sql.format(src1=first, src2=second, join_condition=join_condition, destination=name)
    context.cursor.execute(sql)
    context.cursor.commit()
    return name


def outer_join(first, second, join_variables,  context):
    sql = """SELECT * FROM "{src1}"
             FULL OUTER JOIN "{src2}"
             ON "{join_condition}"
             INTO "{destination}" """
    name = context.get_table_name()
    join_condition = " AND ".join(["".join([first, ".", e, " = ", second, ".", e]) for e, _ in join_variables])
    sql.format(src1=first, src2=second, join_condition=join_condition, destination=name)
    context.cursor.execute(sql)
    context.cursor.commit()
    return name


def cross_join(first, second, context):
    sql = """SELECT * FROM "{src1}"
             CROSS JOIN "{src2}"
             INTO "{destination}" """
    name = context.get_table_name()
    sql.format(src1=first, src2=second, destination=name)
    context.cursor.execute(sql)
    context.cursor.commit()
    return name


def diff(first, second, join_variables, context):
    sql = """SELECT * FROM
            (SELECT "{var_list}" FROM "{src1}"
             EXCEPT
             SELECT "{var_list}" FROM "{src2}")
             INNER JOIN "{src1}"
             INTO "{destination}" """
    name = context.get_table_name()
    var_list = ", ".join([e for e, _ in join_variables])
    sql.format(src1=first, src2=second, var_list=var_list, destination=name)
    context.cursor.execute(sql)
    context.cursor.commit()
    return name


def empty_table(fv, context):
    sql = """CREATE TABLE "{destination}" (
             "{var_list}" );"""
    name = context.get_table_name()
    var_list = [e + " " + i + ",\n" for e, i in fv]
    sql.format(var_list=var_list , destination=name)
    context.cursor.execute(sql)
    context.cursor.commit()
    return name


def table_copy(first, context):
    sql = """SELECT * FROM "{src1}"
             INTO "{destination}" """
    name = context.get_table_name()
    sql.format(src1=first, destination=name)
    context.cursor.execute(sql)
    context.cursor.commit()
    return name
