from typing import Optional
from datetime import datetime
import sqlite3
from dataclasses import dataclass


@dataclass
class Run:
    id: Optional[int]
    dttm: datetime
    completion_token_usage: int
    prompt_token_usage: int
    server_knowledge: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row[0],
            dttm=datetime.fromisoformat(row[1]),
            prompt_token_usage=row[2],
            completion_token_usage=row[3],
            server_knowledge=row[4]
        )


class RunStore:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY,
                dttm TIMESTAMP,
                completion_token_usage INTEGER,
                prompt_token_usage INTEGER,
                server_knowledge TEXT
            )
        ''')
        self.conn.commit()

    def add_run(self, run: Run):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO runs (id, dttm, completion_token_usage, prompt_token_usage, server_knowledge)
            VALUES (?, ?, ?, ?, ?)
        ''', (run.id, run.dttm.isoformat(), run.completion_token_usage, run.prompt_token_usage, run.server_knowledge))
        self.conn.commit()

    def get_runs(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM runs')
        rows = cursor.fetchall()
        return [
            Run.from_row(row)
            for row in rows
        ]
    

    def get_last_run(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM runs ORDER BY dttm DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            return Run.from_row(row)
        else:
            return None

    def close(self):
        self.conn.close()
