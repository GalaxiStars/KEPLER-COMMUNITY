import sqlite3
from PySide6.QtCore import QObject, Signal

class BookmarkManager(QObject):
    bookmarks_updated = Signal()

    def __init__(self, db_file='bookmarks.db'):
        super().__init__()
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks
            (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT)
        ''')
        self.conn.commit()

    def add_bookmark(self, title, url):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO bookmarks (title, url) VALUES (?, ?)", (title, url))
        self.conn.commit()
        self.bookmarks_updated.emit()

    def remove_bookmark(self, bookmark_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        self.conn.commit()
        self.bookmarks_updated.emit()

    def rename_bookmark(self, bookmark_id, new_title):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE bookmarks SET title = ? WHERE id = ?", (new_title, bookmark_id))
        self.conn.commit()
        self.bookmarks_updated.emit()

    def get_bookmarks(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, url FROM bookmarks")
        return cursor.fetchall()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()