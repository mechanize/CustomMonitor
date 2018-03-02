class Context:
    def __init__(self, cursor, names):
        self.cursor = cursor
        self.names = names
        self.name = names[0]
        self.count = 0

    def get_table_name(self):
        self.count += 1
        return self.name + str(self.count)

    def
