class Node:
    def to_str(self):
        pass


class BinaryNode(Node):
    def __init__(self, op, left, right, *sub):
        if sub == tuple():
            self.sub = None
        else:
            self.sub = sub[0]
        self.parent = None
        self.op = op
        self.left = left
        self.right = right
        self.visited = False
        
    def to_str(self):
        return "(" + self.left.to_str() + ") " + self.op + " (" + self.right.to_str() + ")"


class UnaryNode(Node):
    def __init__(self, op, child, *sub):
        if sub == tuple():
            self.sub = None
        else:
            self.sub = sub[0]
        self.parent = None
        self.op = op
        self.child = child
        self.visited = False

    def to_str(self):
        return self.op + " (" + self.child.to_str() + ")"


class Leaf(Node):
    def __init__(self, typ, value):
        self.parent = None
        self.typ = typ
        self.value = value
        self.visited = False

    def to_str(self):
        return self.typ + ": " + self.value
