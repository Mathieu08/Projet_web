# coding: utf8

import sqlite3

class Database(object):
    def __init__(self):
        self.connection = None

    def get_connection(self):
    	if self.connection is None:
            self.connection = sqlite3.connect('db/article.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article")
        articles = cursor.fetchall()
        return [article for article in articles]

    def get_articles_search(self, keyword):
        cursor = self.get_connection().cursor()
        cursor.execute("select titre, date_publication from article where titre like ? or paragraphe like ?", ('%{}%'.format(keyword), '%{}%'.format(keyword)))
        articles = cursor.fetchall()
        return [article for article in articles]