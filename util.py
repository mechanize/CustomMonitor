import re


def parse_signature(file: str) -> [str, (str, str)]:
    res = []
    regex = re.compile(r"[a-z]+\((([a-zA-Z_]+:(int|string|bool))(,[a-zA-Z_]+:(int|string|bool))*)?\)")
    with open(file, "r") as f:
        for line in f.readlines():
            line = "".join(line.split())
            if not regex.match(line):
                raise RuntimeError("Not acceptable signature:", line)
            sig, params = line[:-1].split("(")
            res.append((sig, tuple([e.split(":") for e in params.split(",")])))
    return res


def parse_formula(file: str):
    with open(file, "r") as f:
        lines = f.readlines()
    return "".join(lines)
