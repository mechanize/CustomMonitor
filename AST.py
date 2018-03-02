class Node:
    def to_str(self):
        pass


class BinaryNode(Node):
    def __init__(self, op, left, right):
        self.parent = None
        self.op = op
        self.left = left
        self.right = right
        
    def to_str(self):
        return "(" + self.left.to_str() + ") " + self.op + " (" + self.right.to_str() + ")"


class UnaryNode(Node):
    def __init__(self, op, child):
        self.parent = None
        self.op = op
        self.child = child

    def to_str(self):
        return self.op + " (" + self.child.to_str() + ")"


class Leaf(Node):
    def __init__(self, typ, value):
        self.parent = None
        self.typ = typ
        self.value = value

    def to_str(self):
        return self.typ + ": " + self.value
