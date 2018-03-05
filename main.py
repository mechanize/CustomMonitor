from sys import argv
import util
import Lexer
import MyParser
import sqlite3
from Context import Context

SIGNATURE = 'SIGNATURE'
sig_loc, formula_loc, log_loc = argv[1:4]
rules = []
types = {"int": r"[0-9]+",
         "string": r"[a-zA-Z]+",
         "bool": r"(TRUE|FALSE)"}
for sig, params in util.parse_signature(sig_loc):
    if params == ([''],):
        rules.append((sig + r"\(\)", SIGNATURE))
    else:
        rules.append((sig + r"\(" + ",".join([types.get("string") for e in params]) + r"\)", SIGNATURE))

rules.extend(Lexer.get_rules())
tokens = Lexer.lex(util.parse_formula(formula_loc), rules)
node = MyParser.parse(tokens)
print(node.to_str())

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
context = Context(cursor, ["A", "B"])
