class Node:
    pass


class BinaryNode(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class SingularNode(Node):
    def __init__(self, op, child):
        self.op = op
        self.child = child


class Leaf(Node):
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value