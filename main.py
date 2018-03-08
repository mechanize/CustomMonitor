from sys import argv
import util
import Lexer
import MyParser
import sqlite3
import re
import Evaluator
from Op import get_tuples, Bool
from Context import Context

SIGNATURE = 'SIGNATURE'
sig_loc, formula_loc, log_loc = argv[1:4]
rules = []
types = {"INT": r"[0-9]+",
         "string": r"[a-zA-Z]+",
         "VARCHAR": r"[a-zA-Z]+"}
dic = {}
for sig, params in util.parse_signature(sig_loc):
    if params == [('',)]:
        rules.append((sig + r"\(\)", SIGNATURE))
        dic[sig] = ([], [])
    else:
        rules.append((sig + r"\(" + ",".join([types.get("string") for _ in params]) + r"\)", SIGNATURE))
        dic[sig] = ([e.replace("int", "INT").replace("string", "VARCHAR") for _, e in params], [])

rules.extend(Lexer.get_rules())
tokens = Lexer.lex(util.parse_formula(formula_loc), rules)
node = MyParser.parse(tokens)
print(node.to_str())

conn = sqlite3.connect(":memory:")
context = Context(conn, ["A", "B"])


with open(log_loc, 'r') as f:
    for line in f:
        parse_ts = re.compile(r"@[0-9]+").findall(line)
        if len(parse_ts) == 1:
            ts = int(parse_ts[0][1:])
        else:
            raise RuntimeError("No timestamp found")
        data = {}
        for sig in dic.keys():
            data[sig] = (dic[sig][0].copy(), [])
        for sig in data.keys():
            regex = re.compile(sig + r"\(" + r",\s*".join([types.get(e) for e in data.get(sig)[0]]) + "\)")
            if not data.get(sig)[0]:
                if not regex.findall(line):
                    data.get(sig)[1].append([False])
            for e in regex.findall(line):
                values = []
                for t, k in zip(data.get(sig)[0], e.split("(")[-1][:-1].split(",")):
                    if t == 'INT':
                        values.append(int(k))
                    else:
                        values.append(k)
                data.get(sig)[1].append(values)
        table = Evaluator.evaluate(node, data, context)
        if isinstance(table, Bool):
            if not table.v:
                print("@" + str(ts), True)
        elif table.is_negative:
            for e in get_tuples(table.name, table.fv, context):
                print("@" + str(ts), e)
        else:
            raise RuntimeError("Got infinite violations")
        context.cycle_name()




