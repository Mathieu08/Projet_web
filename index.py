# coding: utf8

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from database import Database

app = Flask(__name__, static_url_path="", static_folder="static")

def get_database():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()
    

@app.route('/')
def accueil():
    articles = get_database().get_articles()
    return render_template('accueil.html', articles=articles)

@app.route('/search', methods=['POST'])
def recherche():
    articles = get_database().get_articles_search(request.form['search'])
    return render_template('recherche.html', articles=articles)