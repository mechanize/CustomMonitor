class Node:
    pass


class BinaryNode(Node):
    def __init__(self, op, left, right):
        self.parent = None
        self.op = op
        self.left = left
        self.right = right


class UnaryNode(Node):
    def __init__(self, op, child):
        self.parent = None
        self.op = op
        self.child = child


class Leaf(Node):
    def __init__(self, typ, value):
        self.parent = None
        self.typ = typ
        self.value = value
