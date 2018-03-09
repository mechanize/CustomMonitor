import sqlite3
import Op


class Context:
    def __init__(self, conn: sqlite3.Connection, names: [str]):
        self.conn = conn
        self.cursor = conn.cursor()
        self.names = [[e, 0] for e in names]
        self.name = names[0][0]
        self.count = 0
        self.var_count = 0
        self.current = []
        self.previous = [Op.Bool(False) for _ in range(30)]
        self.current_ts = 0
        self.previous_ts = 0

    def get_table_name(self):
        self.count += 1
        return self.name + str(self.count)

    def cycle_name(self):

        sql = """DROP TABLE "{name}";"""
        for e in range(1, self.names[-1][1] + 1):
            self.cursor.execute(sql.format(name=(self.names[-1][0] + str(e))))
        self.conn.commit()

        self.names.append([self.name, self.count])
        self.names.pop(0)
        self.name = self.names[0][0]
        self.count = 0
        self.var_count = 0
        self.previous = self.current
        self.current = 0

    def get_current_index(self):
        return len(self.current)

    def get_var_name(self):
        self.var_count += 1
        return "customvar_" + str(self.var_count)

    def set_ts(self, v):
        self.previous_ts = self.current_ts
        self.current_ts = v



