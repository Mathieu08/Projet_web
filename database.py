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

    def get_article(self, identifier):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article where identifiant = ?", (identifier,))
        article = cursor.fetchone()
        if article is None:
            return None
        else:
            return article

    def get_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article")
        articles = cursor.fetchall()
        return [article for article in articles]

    def get_recent_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article where date(date_publication) <= date('now') order by date(date_publication) desc Limit 5")
        articles = cursor.fetchall()
        return [article for article in articles]

    def get_articles_search(self, keyword):
        cursor = self.get_connection().cursor()
        cursor.execute("select titre, date_publication, identifiant from article where titre like ? or paragraphe like ?", ('%{}%'.format(keyword), '%{}%'.format(keyword)))
        articles = cursor.fetchall()
        return [article for article in articles]

    def get_article_by_id(self, article_id):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article where id = ?", (article_id,))
        article = cursor.fetchone()
        if article is None:
            return None
        else:
            return article

    def insert_article(self, article_id, titre, identifiant, auteur, date_pub, paragraphe):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("insert into article(id, titre, identifiant,"
                       "auteur, date_publication, paragraphe)"
                       " values(?, ?, ?, ?, date(?), ?)", (article_id, titre, identifiant, auteur, date_pub, paragraphe))
        connection.commit()

    def update_article(self, titre, identifiant, paragraphe):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("update article set titre = ?, paragraphe = ? where identifiant = ?", (titre, paragraphe, identifiant))
        connection.commit()