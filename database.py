# coding: utf8

#
# Nom: Caouette
# Prenom: Mathieu
# Code permanent: CAOM08109603
# Courriel: caouette.mathieu@courrier.uqam.ca
#

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
        cursor.execute("select * from article where identifiant = ? and "
                       "date(date_publication) <= date('now')", (identifier,))
        article = cursor.fetchone()
        return article

    def get_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article")
        articles = cursor.fetchall()
        return [article for article in articles]

    def get_articles_publie(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article where date(date_publication) "
                       "<= date('now')")
        articles = cursor.fetchall()
        return [article for article in articles]

    def get_recent_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from article "
                       "where date(date_publication) <= date('now') "
                       "order by date(date_publication) desc Limit 5")
        articles = cursor.fetchall()
        return [article for article in articles]

    def get_articles_search(self, keyword):
        cursor = self.get_connection().cursor()
        cursor.execute("select titre, date_publication, identifiant "
                       "from article where date(date_publication) <= "
                       "date('now') and (titre like ? or paragraphe like ?)",
                       ('%{}%'.format(keyword), '%{}%'.format(keyword)))
        articles = cursor.fetchall()
        return [article for article in articles]

    def insert_article(self, titre, identifiant, auteur,
                       date_pub, paragraphe):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("insert into article(titre, identifiant,"
                       "auteur, date_publication, paragraphe)"
                       " values(?, ?, ?, date(?), ?)",
                       (titre, identifiant, auteur,
                        date_pub, paragraphe))
        connection.commit()

    def update_article(self, titre, identifiant, paragraphe):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("update article set titre = ?, paragraphe = ? where "
                       "identifiant = ?", (titre, paragraphe, identifiant))
        connection.commit()

    def get_user_login_info(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute("select salt, hash from users where utilisateur = ?",
                       (username,))
        user = cursor.fetchone()
        return user

    def save_session(self, session_id, username):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("insert into sessions(id_session, utilisateur) "
                       "values(?, ?)", (session_id, username))
        connection.commit()

    def delete_session(self, session_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("delete from sessions where id_session = ?",
                       (session_id,))
        connection.commit()

    def save_token(self, email, token):
        connection = self.get_connection()
        connection.execute("insert into tokens(email, id_token) "
                           "values(?, ?)", (email, token))
        connection.commit()

    def get_email_by_token(self, token):
        cursor = self.get_connection().cursor()
        cursor.execute("select email from tokens where id_token=?",
                       (token,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user

    def create_user(self, username, email, salt, hashed):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("insert into users(utilisateur, email, salt, hash) "
                       "values(?, ?, ?, ?)", (username, email, salt, hashed))
        cursor.execute("delete from tokens where email = ?", (email,))
        connection.commit()

    def reset_password(self, email, salt, hashed):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("update users set salt = ?, hash = ? where email = ?",
                       (salt, hashed, email))
        cursor.execute("delete from tokens where email = ?", (email,))
        connection.commit()

    def get_user_by_email(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute("select * from users where email = ?", (email,))
        user = cursor.fetchone()
        return user
