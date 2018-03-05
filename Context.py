import sqlite3


class Context:
    def __init__(self, cursor: sqlite3.Cursor, names: [str]):
        self.cursor = cursor
        self.names = names
        self.name = names[0]
        self.count = 0
        self.current = []
        self.previous = []

    def get_table_name(self):
        self.count += 1
        return self.name + str(self.count)

    def cycle_name(self):
        self.names.append(self.name)
        self.names.pop(0)
        self.name = self.names[0]
        self.count = 0

    def get_current_index(self):
        return len(self.current)



